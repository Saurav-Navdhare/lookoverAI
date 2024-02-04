docker stop lookover-api
docker build -t lookover-api .
docker run -d -p 5001:5001 --rm --name lookover-api lookover-api