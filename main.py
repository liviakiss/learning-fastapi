# main.py — FastAPI fundamentals, Day 1
# First endpoints, decorators, path parameters, automatic type conversion/validation

from fastapi import FastAPI

app = FastAPI()

# Decorator (@app.get) registers this function into FastAPI's routing table
# by path + HTTP method — doesn't modify the function itself
@app.get("/")
def read_root():
    return {"message": "Hello Lívia"}  # dict auto-converted to JSON

# Path parameter: {name} matched to the `name` param BY NAME
@app.get("/greet/{name}")
def greet(name):
    return {"greeting": f"Hello {name}"}

# Type hint (int) triggers automatic runtime conversion + validation via Pydantic
# Invalid input (e.g. /double/hello) is rejected with a 422 BEFORE this function runs
@app.get("/double/{number}")
def double(number: int):
    return {"result": number * 2}