from pydantic import AnyHttpUrl, BaseModel, EmailStr, ConfigDict, Field


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


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
    url: AnyHttpUrl


class ArticleImportResponse(BaseModel):
    imported_count: int
