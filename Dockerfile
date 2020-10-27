FROM ubuntu

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install vim -y \
    && apt-get install python3.7 -y \
    && apt-get install python3-pip -y \
    && apt-get install git -y \
    && pip3 install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org git+https://github.com/liamcryan/ieuler.git \
    && apt-get install curl -y \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install nodejs -y \
    && apt-get install ruby -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install php -y

RUN useradd -ms /bin/bash -d /usr/local/ieuler ieuler \
    && chown -R ieuler: /usr/local/ieuler

USER ieuler

COPY ./init.sh /usr/local/ieuler/init.sh

WORKDIR /usr/local/ieuler
