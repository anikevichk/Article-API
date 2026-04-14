from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import (
    ArticleCreate,
    ArticleImportResponse,
    ArticleResponse,
    ArticleUpdate,
    ImportFromUrlRequest,
)
from app.security import get_current_user
from app.services.article_import_service import (
    import_articles_from_file_service,
    import_articles_from_url_service,
)
from app.services.article_service import (
    create_article_service,
    delete_article_service,
    get_article_service,
    get_my_articles_service,
    get_subscribed_articles_service,
    list_articles_service,
    update_article_service,
)

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    return list_articles_service(db)


@router.get("/my", response_model=list[ArticleResponse])
def get_my_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_articles_service(db, current_user)


@router.get("/subscribed", response_model=list[ArticleResponse])
def get_subscribed_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_subscribed_articles_service(db, current_user)


@router.post("", response_model=ArticleResponse)
def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_article_service(db, current_user, article_data)


@router.post("/import-file", response_model=ArticleImportResponse)
async def import_articles_from_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await import_articles_from_file_service(db, current_user, file)


@router.post("/import-from-url", response_model=ArticleImportResponse)
def import_articles_from_url(
    data: ImportFromUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_articles_from_url_service(db, current_user, str(data.url))


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    return get_article_service(db, article_id)


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_article_service(db, current_user, article_id, article_data)


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_article_service(db, current_user, article_id)
