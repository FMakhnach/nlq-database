docker volume create --name=db-data

docker-compose build
docker-compose up -d
docker-compose logs -f

pause