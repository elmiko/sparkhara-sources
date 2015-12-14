REPO=172.30.122.181:5000/uber

.PHONY: build push

build:
	docker build -t shiny_squirrel .

push: build
	docker tag -f shiny_squirrel $(REPO)/shiny_squirrel
	docker push $(REPO)/shiny_squirrel
