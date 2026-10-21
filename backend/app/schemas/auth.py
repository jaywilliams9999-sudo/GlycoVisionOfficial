from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class ClinicianOut(BaseModel):
    """Whitelist: password_hash and the lockout fields never leave the server."""
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: ClinicianOut