FROM python:3.10.7-buster

WORKDIR /usr/src

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip awscliv2.zip && \
  ./aws/install

WORKDIR /usr/src/app

RUN curl -sL "https://deb.nodesource.com/setup_18.x" | bash - && \
  apt-get install nodejs
RUN npm install -g aws-cdk

RUN python -m pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true

ENTRYPOINT [ "/bin/bash" ]