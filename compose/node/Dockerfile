FROM docker.io/node:22-bookworm-slim

WORKDIR /app

COPY ./package.json ./package-lock.json /app/

RUN npm ci && npm cache clean --force

ENV PATH=./node_modules/.bin/:$PATH
