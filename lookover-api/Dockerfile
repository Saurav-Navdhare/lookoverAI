FROM node:16

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN chmod +x entrypoint.sh

RUN npm install

EXPOSE 5001

# Assuming entrypoint.sh is in the same directory as Dockerfile
ENTRYPOINT [ "./entrypoint.sh" ]