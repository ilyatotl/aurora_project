run: build
	sudo docker run --name aurora_container -p 8000:8000 aurora_image

build:
	sudo docker build -t aurora_image .

rm_image: rm_container
	sudo docker rmi aurora_image

rm_container: stop
	sudo docker rm aurora_container

stop:
	sudo docker stop aurora_container

image_list:
	sudo docker image ls

container_list:
	sudo docker ps -a