FROM mcr.microsoft.com/playwright/python:v1.31.0-focal

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV \
	IN_DOCKER=1 \
	# Docker user
	USER=user \
	USER_UID=1001 \
	USER_HOME=/home/user \
	USER_DATA_DIR=/home/user/user_data_dir \
	USER_SCRIPTS=/home/user/user_scripts

RUN useradd -s /bin/bash -m -d $USER_HOME -u $USER_UID $USER
USER user

RUN mkdir -p $USER_DATA_DIR $USER_SCRIPTS

# install scrapper package
WORKDIR $USER_HOME
COPY scrapper $USER_HOME/scrapper
COPY setup.py $USER_HOME/setup.py
RUN pip install -e .

CMD waitress-serve --host 0.0.0.0 --port=3000 scrapper:app
