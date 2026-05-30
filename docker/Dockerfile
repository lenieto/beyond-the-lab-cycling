FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git cmake build-essential \
    libopencv-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libhdf5-dev \
    libatlas-base-dev \
    libboost-all-dev \
    libleveldb-dev \
    libsnappy-dev \
    liblmdb-dev \
    python3 python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git /openpose

WORKDIR /openpose

RUN git submodule update --init --recursive --remote

RUN mkdir build && cd build && \
    cmake .. \
    -DBUILD_CAFFE=ON \
    -DGPU_MODE=CPU_ONLY \
    -DUSE_MKL=OFF \
    && make -j$(nproc)

WORKDIR /openpose
