FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
# python==3.10.12, playwright==1.40.0

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt && rm requirements.txt

ENV \
	IN_DOCKER=1 \
	# docker user
	USER=user \
	USER_UID=1001 \
	USER_HOME=/home/user \
	USER_DATA_DIR=/home/user/user_data_dir \
	USER_SCRIPTS=/home/user/user_scripts

RUN useradd -s /bin/bash -m -d $USER_HOME -u $USER_UID $USER
USER $USER

RUN mkdir -p $USER_DATA_DIR $USER_SCRIPTS
COPY --chown=$USER:$USER app $USER_HOME/app

WORKDIR $USER_HOME
CMD python app/main.py
