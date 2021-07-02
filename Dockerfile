FROM quay.io/blueshoe/python3.8-slim as base

FROM base as builder

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y gcc python3-dev libpq-dev g++ git
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt --use-deprecated=legacy-resolver

FROM base

COPY --from=builder /install /usr/local
# additional requirements for prod things
RUN apt update && apt install -y git postgresql-client curl

RUN curl https://get.helm.sh/helm-v3.1.1-linux-amd64.tar.gz | tar xvz \
    && mv linux-amd64/helm /usr/local/bin/helm

RUN helm repo add stable https://charts.helm.sh/stable \
    && helm plugin install https://github.com/nico-ulbricht/helm-multivalues \
    && helm plugin install https://github.com/jkroepke/helm-secrets

RUN mkdir /app
COPY src/ /app
COPY .bumpversion.cfg /app
WORKDIR /app
