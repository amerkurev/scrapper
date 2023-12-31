GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
GITHUB_SHA=$(shell git rev-parse --short HEAD)
REV=$(GIT_BRANCH)-$(GITHUB_SHA)-$(shell date +%Y%m%d-%H:%M:%S)
BIN=scrapper
PWD=$(shell pwd)

info:
	- @echo "revision $(REV)"

# before run: install python packages from requirements.txt
run:
	- @uvicorn --app-dir app main:app --port 3000

test:
	- @$(PWD)/runtest.sh && coverage html

lint:
	- @pylint $(PWD)/app/*

docker:
	- @docker buildx build \
	--build-arg GITHUB_SHA=${GITHUB_SHA} --build-arg GIT_BRANCH=${GIT_BRANCH} \
	-t amerkurev/$(BIN):master --progress=plain .

docker-run: docker
	- @# Using --ipc=host is recommended when using Chrome. Chrome can run out of memory without this flag.
	- @docker run -it --rm --ipc=host -p 3000:3000 -v $(PWD)/user_data:/home/user/user_data -v $(PWD)/user_scripts:/home/user/user_scripts --name $(BIN) amerkurev/$(BIN):master

docker-test: docker
	- @docker run -t --rm --name $(BIN) amerkurev/$(BIN):master ./runtest.sh

docker-lint: docker
	- @docker run -t --rm --name $(BIN) amerkurev/$(BIN):master pylint app/*

.PHONY: info run test lint docker
