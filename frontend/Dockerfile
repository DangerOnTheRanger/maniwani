FROM node:12.12.0-alpine
WORKDIR /frontend-src/

COPY package.json /frontend-src
COPY package-lock.json /frontend-src
RUN npm install
COPY src/ /frontend-src/src
COPY Gulpfile.js /frontend-src
RUN npm run gulp
RUN mv /frontend-src/build /maniwani-frontend
RUN cp -r /frontend-src/node_modules /maniwani-frontend/
WORKDIR /maniwani-frontend
COPY entrypoint.sh /maniwani-frontend
EXPOSE 3000
ENTRYPOINT ["sh", "./entrypoint.sh"]
