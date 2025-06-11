"""
Token controller for DGI API token generation and management
"""
from fastapi import APIRouter
from models.schemas import TokenGenerationRequest, TokenGenerationResponse
from .base_controller import BaseController

router = APIRouter(prefix="/token", tags=["token"])


@router.post("/generate", response_model=TokenGenerationResponse)
async def generate_dgi_token(request: TokenGenerationRequest):
    """Generate DGI API token using API key and secret key"""
    from utils.dgi_token_generator import generate_api_token

    token_data = generate_api_token(
        api_key=request.api_key,
        secret_key=request.secret_key,
        api_time=request.api_time
    )
    
    BaseController.log_operation("GENERATE_TOKEN", f"Generated token for API key {request.api_key[:8]}...")
    return TokenGenerationResponse(**token_data)


@router.post("/refresh", response_model=TokenGenerationResponse)
async def refresh_dgi_token(request: TokenGenerationRequest):
    """Refresh DGI API token with current timestamp"""
    from utils.dgi_token_generator import refresh_token

    token_data = refresh_token(
        api_key=request.api_key,
        secret_key=request.secret_key
    )
    
    BaseController.log_operation("REFRESH_TOKEN", f"Refreshed token for API key {request.api_key[:8]}...")
    return TokenGenerationResponse(**token_data)


@router.get("/current-time")
async def get_current_time():
    """Get current timestamp for token generation"""
    import time
    
    current_time = int(time.time())
    
    BaseController.log_operation("GET_CURRENT_TIME", f"Retrieved current timestamp: {current_time}")
    return {
        "timestamp": current_time,
        "iso_format": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time)),
        "message": "Current server timestamp"
    }


@router.post("/validate")
async def validate_token(request: TokenGenerationRequest):
    """Validate if the provided credentials can generate a valid token"""
    try:
        from utils.dgi_token_generator import generate_api_token
        
        # Try to generate a token to validate credentials
        token_data = generate_api_token(
            api_key=request.api_key,
            secret_key=request.secret_key,
            api_time=request.api_time
        )
        
        BaseController.log_operation("VALIDATE_TOKEN", f"Token validation successful for API key {request.api_key[:8]}...")
        return {
            "valid": True,
            "message": "Credentials are valid and can generate tokens",
            "token_preview": token_data["api_token"][:20] + "...",
            "expires_in": token_data["expires_in"]
        }
        
    except Exception as e:
        BaseController.log_operation("VALIDATE_TOKEN_FAILED", f"Token validation failed for API key {request.api_key[:8]}...: {str(e)}")
        return {
            "valid": False,
            "message": f"Token validation failed: {str(e)}",
            "error": str(e)
        }
