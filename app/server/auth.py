from typing import Annotated

import bcrypt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import settings


security = HTTPBasic()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def basic_auth(request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    username = credentials.username
    password = credentials.password

    creds = request.state.basic_auth_credentials
    if creds is not None:
        if username in creds and check_password(password, creds[username]):
            return username

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )

    return credentials.username


def no_op_auth(request: Request) -> str:
    return 'anonymous'


# Enable or disable authentication based on settings
_credentials = basic_auth if settings.AUTH_ENABLED else no_op_auth

AuthRequired = Annotated[str, Depends(_credentials)]
