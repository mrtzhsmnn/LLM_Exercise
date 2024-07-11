FROM ubuntu:22.04

# Copy files
COPY ./src /home/weather/

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    make \
    cmake \
    build-essential \
    python3-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set CMAKE_PREFIX_PATH environment variable
ENV CMAKE_PREFIX_PATH=/usr

# Create group and user
RUN groupadd -g 2000 weather && \
    useradd -m -u 2000 -g 2000 -s /bin/bash weather

# Upgrade pip and install Python packages
RUN pip3 install --upgrade pip && \
    pip3 install setuptools \
    wheel \
    flask \
    waitress \
    requests \
    pytz \
    geopy

# Clone the repository and install the package
RUN cd / && \
    git clone https://github.com/m0rp43us/openmeteopy && \
    cd openmeteopy/ && \
    pip3 install .

# Create data directory and set permissions
RUN mkdir -p /home/weather/data && \
    chown -R weather:weather /home/weather

WORKDIR /home/weather
USER weather:weather

CMD waitress-serve --port=8080 app:app 
