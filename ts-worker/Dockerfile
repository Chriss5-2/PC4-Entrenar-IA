FROM node:20
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

EXPOSE 5006
EXPOSE 5007
ENV PORT=${PORT}

CMD ["npm", "start"]