from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from database import get_db
from models import ForumPost, ForumComment, PostType

router = APIRouter(prefix="/forum", tags=["forum"])


class PostIn(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    body: str = Field(..., min_length=10)
    post_type: PostType
    area: Optional[str] = None
    nearby_university: Optional[str] = None
    author_name: str = Field(..., min_length=2)
    property_id: Optional[int] = None


class PostOut(BaseModel):
    id: int
    title: str
    body: str
    post_type: PostType
    area: Optional[str]
    nearby_university: Optional[str]
    author_name: str
    upvotes: int
    property_id: Optional[int]
    created_at: str
    comment_count: int = 0

    model_config = {"from_attributes": True}


class CommentIn(BaseModel):
    author_name: str = Field(..., min_length=2)
    content: str = Field(..., min_length=2)


class CommentOut(BaseModel):
    id: int
    post_id: int
    author_name: str
    content: str
    created_at: str

    model_config = {"from_attributes": True}


def _post_out(post: ForumPost, db: Session) -> dict:
    count = db.query(ForumComment).filter(ForumComment.post_id == post.id).count()
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "post_type": post.post_type,
        "area": post.area,
        "nearby_university": post.nearby_university,
        "author_name": post.author_name,
        "upvotes": post.upvotes,
        "property_id": post.property_id,
        "created_at": post.created_at.isoformat() if post.created_at else "",
        "comment_count": count,
    }


@router.get("/", response_model=list[PostOut])
def list_posts(
    post_type: Optional[PostType] = None,
    area: Optional[str] = None,
    nearby_university: Optional[str] = None,
    q: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(ForumPost)
    if post_type:
        query = query.filter(ForumPost.post_type == post_type)
    if area:
        query = query.filter(ForumPost.area.ilike(f"%{area}%"))
    if nearby_university:
        query = query.filter(ForumPost.nearby_university.ilike(f"%{nearby_university}%"))
    if q:
        query = query.filter(
            ForumPost.title.ilike(f"%{q}%") | ForumPost.body.ilike(f"%{q}%")
        )
    posts = query.order_by(ForumPost.created_at.desc()).offset(skip).limit(limit).all()
    return [_post_out(p, db) for p in posts]


@router.post("/", response_model=PostOut, status_code=201)
def create_post(payload: PostIn, db: Session = Depends(get_db)):
    post = ForumPost(**payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_out(post, db)


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_out(post, db)


@router.post("/{post_id}/upvote")
def upvote_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.upvotes += 1
    db.commit()
    return {"upvotes": post.upvotes}


@router.get("/{post_id}/comments", response_model=list[CommentOut])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(ForumComment)
        .filter(ForumComment.post_id == post_id)
        .order_by(ForumComment.created_at)
        .all()
    )
    return [
        {
            "id": c.id,
            "post_id": c.post_id,
            "author_name": c.author_name,
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else "",
        }
        for c in comments
    ]


@router.post("/{post_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(post_id: int, payload: CommentIn, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = ForumComment(post_id=post_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_name": comment.author_name,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else "",
    }
