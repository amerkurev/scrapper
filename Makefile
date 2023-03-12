B=$(shell git rev-parse --abbrev-ref HEAD)
BRANCH=$(subst /,-,$(B))
GITREV=$(shell git describe --abbrev=7 --always --tags)
REV=$(GITREV)-$(BRANCH)-$(shell date +%Y%m%d-%H:%M:%S)
BIN=scrapper
PWD=$(shell pwd)

UNAME_S:=$(shell uname -s)
GOOS:=
ifeq ($(UNAME_S),Darwin)
	GOOS=darwin
else
	GOOS=linux
endif

info:
	- @echo "os $(GOOS)"
	- @echo "revision $(REV)"

# flask
# before run: install python packages from requirements.txt
debug-server:
	- @flask --app app/main.py run --port 3000 --debug

## Docker ##
docker:
	docker build -t amerkurev/$(BIN):master --progress=plain .

docker-run: docker
	docker run -d --rm --ipc=host -p 3000:3000 -v $(PWD)/user_data_dir:/home/user/user_data_dir --name $(BIN) amerkurev/$(BIN):master

.PHONY: info build run clean test docker dist
