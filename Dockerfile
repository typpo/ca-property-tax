FROM node:12-stretch-slim

ENV NODE_ENV production
ENV LOG_LEVEL debug

WORKDIR /app

COPY package*.json ./
COPY yarn.lock .

RUN yarn install --production --pure-lockfile

COPY app/ app/
COPY server/ server/
COPY data/*.csv.gz data/

EXPOSE 13000

ENTRYPOINT ["node", "server/index.js"]
