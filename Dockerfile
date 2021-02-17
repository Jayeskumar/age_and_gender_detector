FROM python:3.6-slim-stretch

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    make \
    cmake \
    git \
    wget \
    curl \
    zip \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . ./

RUN make unittest

CMD ["make", "prod"]
