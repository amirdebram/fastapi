import asyncio
import gzip
import json
import logging
import redis.asyncio as redis

from fastapi import Request
from fastapi.responses import JSONResponse
from functools import wraps

from app.dependencies.__config__ import settings

class RedisClientManager:
    def __init__(self):
        self.host = settings.redis_host
        self.port = settings.redis_port
        self.password = settings.redis_password
        self.client = None
        self.pool = None

    async def init_client(self) -> None:
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            password=self.password,
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
        self.client = redis.Redis(connection_pool=self.pool)

    async def close_client(self) -> None:
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect(inuse_connections=True)

    async def get(self, key: str) -> str:
        return await retry_operation(lambda: self.client.get(key))

    async def set(self, key: str, value: str) -> None:
        await retry_operation(lambda: self.client.set(key, value))

    async def setex(self, key: str, expiration: int, value: str) -> None:
        try:
            await self.client.setex(key, expiration, value)
        except redis.RedisError as e:
            logging.error(f"Redis error setting key with expiration {key}: {str(e)}")
    
    async def set_compressed_cache(self, key: str, data: bytes, expiration: int = None):
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        compressed_data = gzip.compress(json.dumps(json.loads(data)).encode('utf-8'))
        if expiration:
            await redis_manager.setex(key, expiration, compressed_data)
        else:
            await redis_manager.set(key, compressed_data)

    async def get_compressed_cache(self, key: str):
        compressed_data = await redis_manager.get(key)
        if compressed_data:
            return json.loads(gzip.decompress(compressed_data).decode('utf-8'))
        return None
    

    async def exists(self, key: str) -> bool:
        try:
            return await self.client.exists(key)
        except redis.RedisError as e:
            logging.error(f"Redis error checking existence of key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except redis.RedisError as e:
            logging.error(f"Redis error deleting key {key}: {str(e)}")

    async def clear_all_cache(self) -> None:
        try:
            await self.client.flushdb()
            logging.info("Redis database cleared successfully.")
        except redis.RedisError as e:
            logging.error(f"Failed to clear Redis database: {str(e)}")
            raise  # Re-raise after logging

    async def __aenter__(self) -> 'RedisClientManager':
        try:
            await self.init_client()
        except Exception as e:
            logging.error(f"Failed to initialize Redis client: {str(e)}")
            raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await self.close_client()
        except Exception as e:
            logging.error(f"Error during Redis client cleanup: {str(e)}")


redis_manager = RedisClientManager()

async def retry_operation(operation, retries=3, delay=1):
    for i in range(retries):
        try:
            return await operation()
        except (redis.RedisError, ConnectionError, TimeoutError) as e:
            if i < retries - 1:
                logging.warning(f"Retrying operation due to: {str(e)}")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise e

def cache_response(expiration: int = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Generate a cache key based on the function name and path parameters
            cache_key = func.__name__.lower()

            path_params = request.path_params
            if path_params:
                cache_key += "_" + "_".join(str(v).lower() for v in path_params.values())

            # Check if the response is already cached
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                try:
                    return JSONResponse(content=json.loads(cached_data))
                except json.JSONDecodeError:
                    # If cached data is not valid JSON, ignore it and proceed to regenerate
                    pass

            # If not cached or invalid, call the function and cache its response
            response = await func(request, *args, **kwargs)

            # Store response in cache
            if expiration:
                await redis_manager.setex(cache_key, expiration, response.body)
            else:
                await redis_manager.set(cache_key, response.body)
            
            # Return the original response
            return response

        return wrapper
    return decorator

def cache_response_with_compression(expiration: int = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Generate cache key based on function name and path parameters
            cache_key = func.__name__.lower()
            path_params = request.path_params
            if path_params:
                cache_key += "_" + "_".join(str(v).lower() for v in path_params.values())

            # Attempt to retrieve cached data
            cached_data = await redis_manager.get_compressed_cache(cache_key)
            if cached_data:
                return JSONResponse(content=cached_data)

            # Call the function to get fresh data if cache is empty
            response = await func(request, *args, **kwargs)

            # Store response in compressed cache
            await redis_manager.set_compressed_cache(cache_key, response.body, expiration)

            # Return the original response
            return response

        return wrapper
    return decorator
