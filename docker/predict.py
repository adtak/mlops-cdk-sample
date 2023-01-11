import pickle

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class InvocationsRequest(BaseModel):
    x1: int
    x2: int


@app.get("/ping")
def ping():
    return {}


@app.post("/invocations")
def invocations(request: InvocationsRequest):
    with open("/opt/ml/model/model.pickle", "rb") as f:
        model = pickle.load(f)
    result = model.predict([[request.x1, request.x2]])
    return {"result": result.tolist()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
