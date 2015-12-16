REPO=172.30.122.181:5000/uber

.PHONY: build push build-pathfinder build-master push-pathfinder push-master

build: build-pathfinder build-master
push: push-pathfinder push-master

build-pathfinder:
	docker build -t caravan_pathfinder -f Dockerfile.pathfinder .
build-master:
	docker build -t caravan_master -f Dockerfile.master .

push-pathfinder: build-pathfinder
	docker tag -f caravan_pathfinder $(REPO)/caravan_pathfinder
	docker push $(REPO)/caravan_pathfinder

push-master: build-master
	docker tag -f caravan_master $(REPO)/caravan_master
	docker push $(REPO)/caravan_master
