"""
Authentication API Endpoints
Handles user registration, login, logout, token refresh, and password management
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import get_db
from app.models.shared import User, Tenant, UserStatusEnum
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    LoginResponse,
    TokenResponse,
    UserResponse,
    MessageResponse
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_token_type
)
from app.core.config import settings
from app.api.deps import get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입 API

    - **tenant_id**: 테넌트 ID (필수)
    - **username**: 사용자명 (3-50자, 영문/숫자/언더스코어/하이픈)
    - **email**: 이메일 주소
    - **password**: 비밀번호 (8자 이상, 대소문자+숫자 포함)
    - **full_name**: 전체 이름 (선택)
    - **phone**: 전화번호 (선택)
    """
    try:
        # 1. Tenant 존재 확인
        tenant = db.query(Tenant).filter(
            Tenant.id == user_data.tenant_id,
            Tenant.is_active == True,
            Tenant.is_deleted == False
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found or is inactive"
            )

        # 2. 이메일 중복 확인 (테넌트 내에서)
        existing_user = db.query(User).filter(
            User.tenant_id == user_data.tenant_id,
            User.email == user_data.email,
            User.is_deleted == False
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered in this tenant"
            )

        # 3. 사용자명 중복 확인 (테넌트 내에서)
        existing_username = db.query(User).filter(
            User.tenant_id == user_data.tenant_id,
            User.username == user_data.username,
            User.is_deleted == False
        ).first()

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken in this tenant"
            )

        # 4. 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)

        # 5. 사용자 생성
        new_user = User(
            tenant_id=user_data.tenant_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            status=UserStatusEnum.ACTIVE,
            is_superuser=False,
            is_email_verified=False,
            created_by="system"
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인 API

    - **email**: 이메일 주소
    - **password**: 비밀번호
    - **tenant_id**: 테넌트 ID (선택, 없으면 이메일로 조회된 첫 번째 사용자)

    Returns:
        - **user**: 사용자 정보
        - **tokens**: Access Token + Refresh Token
    """
    try:
        # 1. 사용자 조회
        query = db.query(User).filter(
            User.email == login_data.email,
            User.is_deleted == False
        )

        # 테넌트 ID가 제공된 경우 필터 추가
        if login_data.tenant_id:
            query = query.filter(User.tenant_id == login_data.tenant_id)

        user = query.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # 2. 비밀번호 검증
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # 3. 계정 상태 확인
        if not user.is_active or user.status != UserStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User account is {user.status}"
            )

        # 4. JWT 토큰 생성
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "tenant_id": user.tenant_id,
                "is_superuser": user.is_superuser
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id)
            }
        )

        # 5. 마지막 로그인 시간 업데이트
        user.last_login_at = datetime.now(timezone.utc)
        user.updated_by = user.username
        db.commit()
        db.refresh(user)

        # 6. 응답 생성
        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    토큰 갱신 API

    - **refresh_token**: 리프레시 토큰

    Returns:
        새로운 Access Token + Refresh Token
    """
    try:
        # 1. Refresh Token 검증
        try:
            payload = decode_token(refresh_data.refresh_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # 2. 토큰 타입 확인
        if not validate_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # 3. 사용자 ID 추출
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user_id = int(user_id_str)

        # 4. 사용자 조회
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.is_deleted == False,
            User.status == UserStatusEnum.ACTIVE
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or is inactive"
            )

        # 5. 새 토큰 생성
        new_access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "tenant_id": user.tenant_id,
                "is_superuser": user.is_superuser
            }
        )

        new_refresh_token = create_refresh_token(
            data={
                "sub": str(user.id)
            }
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    로그아웃 API

    Note: JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없습니다.
    클라이언트에서 토큰을 삭제해야 합니다.
    향후 Redis를 사용한 블랙리스트 기능을 추가할 수 있습니다.
    """
    return MessageResponse(
        message="Logout successful",
        detail="Please remove the token from client storage"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    현재 로그인한 사용자 정보 조회 API

    Returns:
        현재 사용자의 상세 정보
    """
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    프로필 업데이트 API

    - **full_name**: 전체 이름 (선택)
    - **phone**: 전화번호 (선택)
    - **bio**: 자기소개 (선택)
    - **profile_image_url**: 프로필 이미지 URL (선택)
    """
    try:
        # 업데이트할 필드만 변경
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name

        if profile_data.phone is not None:
            current_user.phone = profile_data.phone

        if profile_data.bio is not None:
            current_user.bio = profile_data.bio

        if profile_data.profile_image_url is not None:
            current_user.profile_image_url = profile_data.profile_image_url

        current_user.updated_by = current_user.username
        db.commit()
        db.refresh(current_user)

        return UserResponse.model_validate(current_user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.put("/password", response_model=MessageResponse)
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경 API

    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (8자 이상, 대소문자+숫자 포함)
    """
    try:
        # 1. 현재 비밀번호 확인
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # 2. 새 비밀번호 해싱
        new_hashed_password = get_password_hash(password_data.new_password)

        # 3. 비밀번호 업데이트
        current_user.hashed_password = new_hashed_password
        current_user.updated_by = current_user.username
        db.commit()

        return MessageResponse(
            message="Password changed successfully",
            detail="Please login again with the new password"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


# ============================================================================
# Additional Endpoints (Future Implementation)
# ============================================================================

@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    이메일 인증 API (미구현)

    향후 이메일 발송 기능과 함께 구현 예정
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification not implemented yet"
    )


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    비밀번호 찾기 API (미구현)

    향후 이메일 발송 기능과 함께 구현 예정
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not implemented yet"
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    비밀번호 재설정 API (미구현)

    향후 이메일 발송 기능과 함께 구현 예정
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not implemented yet"
    )
