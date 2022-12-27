FROM python:3.10.7-slim-buster

ADD preprocess.py /

ENTRYPOINT ["python3", "/preprocess.py"]