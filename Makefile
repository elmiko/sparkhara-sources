REPO=172.30.122.181:5000/uber

.PHONY: build push

build:
	$(MAKE) -C shiny_squirrel build
	$(MAKE) -C whirlwind_caravan build

push:
	$(MAKE) -C shiny_squirrel push
	$(MAKE) -C whirlwind_caravan push
