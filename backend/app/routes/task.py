import math
from collections.abc import Sequence
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query,status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate,PaginatedTaskResponse
from app.services import task_service

router = APIRouter()


@router.post("/add", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return task_service.create_task(db, task_in, owner_id=current_user.id)


@router.get("/list", response_model=PaginatedTaskResponse)
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    is_completed: bool | None = Query(None, description="Filter by completion status"),
    search: str | None = Query(None, min_length=1, description="Search keyword in title or description"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
):
    tasks, total_count = task_service.get_user_tasks(
        db,
        owner_id=current_user.id,
        is_completed=is_completed,
        search=search,
        page=page,
        page_size=page_size,
    )
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    return PaginatedTaskResponse(
        items=tasks,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/show/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    task = task_service.get_task_by_id(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/update/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    task = task_service.get_task_by_id(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_service.update_task(db, db_task=task, task_in=task_in)


@router.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    task = task_service.get_task_by_id(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task_service.delete_task(db, db_task=task)
