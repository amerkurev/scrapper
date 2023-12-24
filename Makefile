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

# before run: install python packages from requirements.txt
run:
	- @uvicorn --app-dir app main:app --port 3000

test:
	- @$(PWD)/tests.sh

docker:
	- @docker build -t amerkurev/$(BIN):master --progress=plain .

docker-run: docker
	- @# Using --ipc=host is recommended when using Chrome. Chrome can run out of memory without this flag.
	- @docker run -it --rm --ipc=host -p 3000:3000 -v $(PWD)/user_data_dir:/home/user/user_data_dir -v $(PWD)/user_scripts:/home/user/user_scripts --name $(BIN) amerkurev/$(BIN):master || true

docker-test: docker
	- @docker run -t --rm --name $(BIN) amerkurev/$(BIN):master ./tests.sh

.PHONY: info run test docker
