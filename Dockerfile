FROM ubuntu:precise
MAINTAINER Azavea

# Quiet things down a bit
ENV DEBIAN_FRONTEND noninteractive

# Install dependencies
RUN apt-get update
RUN apt-get install -y build-essential wget python python-dev python-setuptools
RUN apt-get -y install libffi-dev
RUN apt-get -y purge openssl
RUN apt-get -y autoremove
RUN easy_install pip

# Install OpenSSL from source
RUN mkdir /tmp/openssl
WORKDIR /tmp/openssl
RUN wget http://www.openssl.org/source/openssl-1.0.1g.tar.gz
RUN tar -xzf openssl-1.0.1g.tar.gz

WORKDIR openssl-1.0.1g
RUN ./config
RUN make depend
RUN make
RUN make install

# Clean up OpenSSL
WORKDIR /
RUN rm -rf /tmp/openssl

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN pip install -r requirements.txt

# Make project source available
ADD . /opt/updater
WORKDIR /opt/updater

# Execute updater
CMD ["python", "NOLAUpdate.py"]
