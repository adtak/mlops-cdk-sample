FROM python:3.10.7-slim-buster

RUN pip install fastapi uvicorn[standard] scikit-learn
ADD predict.py /

ENTRYPOINT ["python3", "/predict.py"]