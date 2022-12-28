FROM python:3.10.7-slim-buster

RUN pip install fastapi 
RUN pip install uvicorn[standard]
ADD predict.py /

ENTRYPOINT ["python3", "/predict.py"]