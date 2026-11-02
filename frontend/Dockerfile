FROM node:22.23.4-alpine3.23

WORKDIR /app
COPY package.json /app/package.json
RUN npm install
COPY . /app

CMD ["npm", "run", "dev"]
