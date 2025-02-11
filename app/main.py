from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.dependencies.__config__ import settings
from app.dependencies.__helpers__ import lifespan

from app.routers import router_auth, router_index, router_users


def get_app() -> FastAPI:
    """Create and configure a FastAPI app with middleware, static files, and routes."""
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)

    # Generate list of allowed origins for all valid IPs in the range
    # origins = [
    #     "http://localhost:3000",
    #     "https://dev.crystallogic.org",
    #     "https://dev.crystallogic.org:8080",
    # ]

    # Add middleware for rate limiting, HTTPS redirection, and trusted hosts
    # app.add_middleware(CORSMiddleware, 
    #                    allow_origins=origins, 
    #                    allow_credentials=True, 
    #                    allow_methods=["*"],
    #                    allow_headers=["*"],
    #                    )
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
    # app.add_middleware(HTTPSRedirectMiddleware)
    # app.add_middleware(TrustedHostMiddleware, allowed_hosts=["dev.crystallogic.org", "dev.crystallogic.org:8080", "localhost:3000"])

    # Include various routers
    app.include_router(router_index.router)
    app.include_router(router_auth.router)
    app.include_router(router_users.router)
    
    return app

app = get_app()
