from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    db_task = Task(**task_in.model_dump(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_user_tasks(
    db: Session,
    owner_id: int,
    is_completed: bool | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[Sequence[Task], int]:
    # 1. Base query scoped to user
    stmt = select(Task).where(Task.owner_id == owner_id)

    # 2. Apply optional filters
    if is_completed is not None:
        stmt = stmt.where(Task.is_completed == is_completed)

    if search:
        # Case-insensitive title/description search using ILIKE in Postgres
        stmt = stmt.where(
            (Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))
        )

    # 3. Calculate total count before pagination
    total_count = len(db.scalars(stmt).all())

    # 4. Apply sorting and pagination (LIMIT & OFFSET)
    offset = (page - 1) * page_size
    stmt = stmt.order_by(Task.created_at.desc()).offset(offset).limit(page_size)

    tasks = db.scalars(stmt).all()
    return tasks, total_count


def get_task_by_id(db: Session, task_id: int, owner_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    return db.scalar(stmt)


def update_task(db: Session, db_task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, db_task: Task) -> None:
    db.delete(db_task)
    db.commit()
