docker-up: build
	sudo docker-compose up

docker-up-detached: build
	sudo docker-compose up -d

build:
	sudo docker-compose build

docker-down: 
	sudo docker-compose down