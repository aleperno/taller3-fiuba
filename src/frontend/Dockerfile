FROM node:18-alpine

WORKDIR /code/

COPY public/ /code/public
COPY package.json /code/
COPY package-lock.json /code/
COPY tsconfig.json /code/

RUN npm install

CMD ["npm", "start"]

