from pydantic import BaseModel, EmailStr, ConfigDict


class ArticleCreate(BaseModel):
    title: str
    content: str


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class SubscriptionResponse(BaseModel):
    id: int
    subscriber_id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    article_id: int
    message: str
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class ImportFromUrlRequest(BaseModel):
    url: str


class ArticleImportResponse(BaseModel):
    imported_count: int