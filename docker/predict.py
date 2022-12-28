import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def ping():
    return {}


@app.post("/invocations")
def transformation():
    return {"invocated": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
