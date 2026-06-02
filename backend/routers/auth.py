from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models.schemas import RegisterRequest, LoginRequest, RegisterResponse, LoginResponse
from services.auth_service import hash_password, verify_password, create_access_token, decode_token
from services.supabase_service import (
    create_user, get_user_by_email,
    create_company, get_company_by_invite_code, get_company_by_id
)

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register")
def register(request: RegisterRequest):
    """
    Two flows:
    1. Admin — provides company_name → creates new company, registers as admin
    2. Employee — provides invite_code → joins existing company, registers as user
    """
    # Validate email
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    # Validate password
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Check email not already registered
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Determine flow
    if request.company_name:
        # ADMIN FLOW — create new company
        company = create_company(request.company_name)
        company_id = company["id"]
        role = "admin"

    elif request.invite_code:
        # EMPLOYEE FLOW — join existing company
        company = get_company_by_invite_code(request.invite_code)
        if not company:
            raise HTTPException(status_code=404, detail="Invalid invite code")
        company_id = company["id"]
        role = "user"

    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either company_name (admin) or invite_code (employee)"
        )

    # Create user
    hashed = hash_password(request.password)
    user = create_user(request.email, hashed, company_id=company_id, role=role)

    return {
        "success": True,
        "message": f"Account created successfully as {role}",
        "user_id": user["id"],
        "email": user["email"],
        "role": role,
        "company_id": company_id,
        "invite_code": company["invite_code"] if role == "admin" else None
    }

@router.post("/login")
def login(request: LoginRequest):
    """
    Logs in user and returns JWT token with role and company_id.
    """
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Include role and company_id in token
    token = create_access_token(data={
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"],
        "company_id": str(user["company_id"])
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "company_id": user["company_id"]
    }

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts current user from JWT token.
    Now includes role and company_id.
    """
    try:
        payload = decode_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "company_id": payload.get("company_id")
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency — only allows admin users.
    Use this on upload/delete endpoints.
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can perform this action"
        )
    return user