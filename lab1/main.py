from typing import Optional
from fastapi import FastAPI

app = FastAPI()
@app.get("/factorial/{num}")
def get_factorial(num1: int):

    if num1 < 0:
        return {"nput cannot be negative"}
    
    if num1 == 0:
        return {"result": False}
    result = 1
    a = 1

    while a <= num1:
        result *= a
        a += 1
    return {"result": result}
