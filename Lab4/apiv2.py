from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
# Create FastAPI instance
app = FastAPI()
def api_key_check(api_key: str = None):
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return True

# Shared database for tasks
task_db = [
    {"task_id": 1, "task_name": "Laboratory Activity", "task_desc": "Create Lab Act 1", "is_finished": False},
    {"task_id": 2, "task_name": "Laboratory Activity", "task_desc": "Create Lab Act 2", "is_finished": False},
    {"task_id": 3, "task_name": "Laboratory Activity", "task_desc": "Create Lab Act 3", "is_finished": False}
]

# Pydantic model for Task
class Task(BaseModel):
    task_id: int
    task_name: str
    task_desc: str
    is_finished: bool


# Helper functions for task operations
def find_task_by_id(task_id: int):
    return next((task for task in task_db if task["task_id"] == task_id), None)


# Version 1 Router
v1_router = APIRouter()

# get
@v1_router.get("/tasks/{task_id}") 
def read_users(task_no: Optional[int] = None):
    # Check if the task_id is provided
    if task_no is not None:        
        # Find user by task_id
        if task_no < 1:
                return {"error": "task Id should not be lower than 1!"}
        
        for u in task_db:
            # If the task_id matches the value in the task_db
            # Return value of task
            if u["task_id"] == task_no:
                return {"status": "ok", "result" : u}
     
        # Return value if task is not found
        return{"error": "The task id cannot found in the database!"}

    return {"error": "You need to provide the task id to view the data from"}

# post
@v1_router.post("/tasks") 
def create_task(task: Task): 
    # Check of task ID is available in the task_db list
    # IF already existing, return error
    if any(u['task_id'] == task.task_id for u in task_db):
        return {"error": "Task Id is already existing"}
    
    # If task_id is not yet existing, we append the passed Task object to the task_db list
    # Take note that we are casting the task object to dict so that it matches the data type
    # Of the contents of task_db
    task_db.append(dict(task))
    return {"status": "ok"}

# patch
@v1_router.patch("/tasks/{task_id}")
def update_task(task_id: int, task: Task):  
     # Check if the Task_id is provided
    if task_id:
        # Find task by task_id
        for idx, u in enumerate(task_db):
            # If the task_id in the task_db matches the inputted task_id from the parameter
            # Update the values of the keys in task_db
            # Then return a status "ok" and show the updated data
            if u["task_id"] == task_id:
                task_db[idx]['task_id'] = task.task_id 
                task_db[idx]['task_name'] = task.task_name
                task_db[idx]['task_desc'] = task.task_desc
                task_db[idx]['is_finished'] = task.is_finished

                return {"status": "ok", "updated_data": task_db[idx]}
    
    return {"error": "Task not found in the database. Cannot update data"}

# delete
@v1_router.delete("/tasks/{task_id}")
def delete_task(task_id: int): # Takes a path parameter task_id that can take integer values
     # Check if the task_id is provided
    if task_id:
        # Find task by task_id
        for idx, u in enumerate(task_db):
            # If the task_id in the task_db matches the inputted task_id from the parameter
            # Remove the task object in task_db
            # Then return a status "ok" and show the removed data
            if u["task_id"] == task_id:
                task_db.remove(u)
                return {"status": "ok", "removed_data": u}
    
    # Return an error message if there is no task found
    return {"error": "Task Id not found in the database. Cannot delete the data"}

# Version 2 Router
v2_router = APIRouter()

@v2_router.get("/tasks/{task_id}")
def get_task_v2(task_id: int):
    task = find_task_by_id(task_id)
    if task:
        return {"status": "ok", "result": task}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@v2_router.post("/tasks", status_code=status.HTTP_201_CREATED) 
def create_task(task: Task): 
    # Check of task ID is available in the task_db list
    # IF already existing, return error
    if any(u['task_id'] == task.task_id for u in task_db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task Id is already existing")
    if task.task_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task number it should be 1 and up")
    # If task_id is not yet existing, we append the passed Task object to the task_db list
    # Take note that we are casting the task object to dict so that it matches the data type
    # Of the contents of task_db
    task_db.append(dict(task))
    return {"status": "Task added successfully"}


@v2_router.patch("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_task_v2(task_id: int, task: Task):
    for idx, existing_task in enumerate(task_db):
        if existing_task["task_id"] == task_id:
            task_db[idx] = task.dict()
            return {"status": "ok", "updated_task": task_db[idx]}
        if task.task_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task number it should be 1 and up")
    raise HTTPException(status_code=404, detail="Task not found")

@v2_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_v2(task_id: int):
    task = find_task_by_id(task_id)
    if task:
        task_db.remove(task)
        return {"status": "ok", "removed_task": task}
    if task_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task number it should be 1 and up")
    raise HTTPException(status_code=404, detail="Task not found")



# Register routers with prefixes
app.include_router(v1_router, prefix="/v1", tags=["Version 1"])
app.include_router(v2_router, prefix="/v2", tags=["Version 2"])
