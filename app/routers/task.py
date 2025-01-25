from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser, CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify
router = APIRouter(prefix="/task", tags=["task"])

@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task)).scalars().all()
    return tasks

@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):

    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found')

    return task


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id: int):
    task = db.scalar(select(Task).where(create_task.title == Task.title))
    user = db.scalar(select(User).where(User.id == user_id))
    if task is True:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail='This task is registered')
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   user_id=user_id,
                                   slug=slugify(create_task.title)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.put("/update")
async def update_task(task_id: int, update_task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    up_task = db.scalar(select(Task).where(Task.id == task_id))
    if up_task is None:
        raise HTTPException(status_code=404, detail="Task was not found")
    db.execute(update(Task).where(Task.id == task_id).values(title=update_task.title,
                                                             content=update_task.content,
                                                             priority=update_task.priority))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful'}


@router.delete("/delete")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    del_task = db.scalar(select(Task).where(Task.id == task_id))
    if del_task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task delete is successful'
    }