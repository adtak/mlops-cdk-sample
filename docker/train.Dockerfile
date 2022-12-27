FROM python:3.10.7-slim-buster

RUN pip3 install pandas scikit-learn
ADD train.py /

ENTRYPOINT ["python3", "/train.py"]