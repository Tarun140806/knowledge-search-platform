from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models.schemas import RegisterRequest, LoginRequest, RegisterResponse, LoginResponse
from services.auth_service import hash_password, verify_password, create_access_token, decode_token
from services.supabase_service import create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    """
    Creates a new user account.
    """
    # Check if email already exists
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and save user
    hashed = hash_password(request.password)
    user = create_user(request.email, hashed)

    return {
        "success": True,
        "message": "Account created successfully",
        "user_id": user["id"],
        "email": user["email"]
    }

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Logs in a user and returns a JWT token.
    """
    # Check if user exists
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token
    token = create_access_token(data={
        "sub": user["id"],
        "email": user["email"]
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["id"],
        "email": user["email"]
    }

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency — extracts current user from JWT token.
    Use this in any protected endpoint.
    """
    try:
        payload = decode_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email")
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")