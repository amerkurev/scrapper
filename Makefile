ifdef GITHUB_REF
    # CI environment - use provided ref
    GIT_TAG=$(shell echo $(GITHUB_REF) | cut -d'/' -f3)
else
    # Local environment - calculate from git
	GIT_TAG=$(shell git describe --tags --abbrev=0 2>/dev/null || git rev-parse --abbrev-ref HEAD)
endif

ifdef GITHUB_SHA
	# CI environment - use provided sha
	GIT_SHA=$(GITHUB_SHA)
else
	# Local environment - calculate from git
	GIT_SHA=$(shell git rev-parse --short HEAD)
endif

REV=$(GIT_TAG)-$(GIT_SHA)
PWD=$(shell pwd)
BIN=scrapper

info:
	- @echo "revision $(REV)"

pip-sync:
	- @pip-compile requirements.in
	- @pip-sync requirements.txt

build:
	- @docker buildx build --load --build-arg GIT_SHA="${GIT_SHA}" --build-arg GIT_TAG="${GIT_TAG}" -t amerkurev/$(BIN):latest --progress=plain .

lint:
	- @ruff check app

fmt: lint
	- @ruff format app

test:
	- @docker run --rm -t -v $(PWD)/app:/home/pwuser/app amerkurev/$(BIN) ./pytest.sh

cov:
	- @docker run --rm -t -v $(PWD)/app:/home/pwuser/app amerkurev/$(BIN) coverage html

dev: build
	- @# Using --ipc=host is recommended when using Chrome. Chrome can run out of memory without this flag.
	- @docker run \
	  -it \
	  --rm \
	  --ipc=host \
	  --env-file=.env \
	  -v $(PWD)/app:/home/pwuser/app \
	  -v $(PWD)/user_data:/home/pwuser/user_data \
	  -v $(PWD)/user_scripts:/home/pwuser/user_scripts \
	  --name $(BIN) \
	  -p 3000:3000 \
	  amerkurev/$(BIN)

.PHONY: info build lint fmt test cov dev
