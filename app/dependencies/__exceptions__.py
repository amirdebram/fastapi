from fastapi import HTTPException, status

def bad_request(detail: str):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def no_content(detail: str):
    return HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def unauthorized(detail: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def forbidden(detail: str):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def conflict(detail: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

