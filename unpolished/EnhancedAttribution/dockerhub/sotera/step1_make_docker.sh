#!/bin/bash
wget http://ea-refs.s3.amazonaws.com/NVIDIA-Linux-x86_64-367.57.run
docker build -f ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe.docker -t sotera/ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe:1 .

docker login

docker push sotera/ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe:1
