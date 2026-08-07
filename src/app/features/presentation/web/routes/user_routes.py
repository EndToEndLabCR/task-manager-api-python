from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.features.application.dtos.user_dto import (
    UserResponse,
    UserCreateRequest,
    DeleteResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
)
from src.app.features.application.exceptions.user_exception import (
    UserDoesNotExistException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from src.app.features.application.use_cases.create_user import CreateUserUseCase
from src.app.features.application.use_cases.delete_user import DeleteUserUseCase
from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase
from src.app.features.application.use_cases.login_user import LoginUseCase, TooManyLoginAttemptsException
from src.app.features.application.use_cases.refresh_token import RefreshTokenUseCase
from src.app.features.presentation.web.dependencies import (
    get_register_user_use_case,
    get_login_use_case,
    get_delete_user_use_case,
    get_user_by_id_use_case,
    get_refresh_token_use_case,
    get_current_user,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(str(user_id))

    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    use_case: CreateUserUseCase = Depends(get_register_user_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(payload)

    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponse:
    try:
        return await use_case.execute(payload.email, payload.password)

    except TooManyLoginAttemptsException as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))

    except InvalidCredentialsException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh-token", response_model=LoginResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> LoginResponse:
    try:
        return await use_case.execute(payload.refresh_token)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete("/{user_id}", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> DeleteResponse:
    try:
        return await use_case.execute(str(user_id))

    except UserDoesNotExistException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
