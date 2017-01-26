#!/bin/bash
wget http://ea-refs.s3.amazonaws.com/NVIDIA-Linux-x86_64-367.57.run
docker build -f ubuntu-cudnn4.docker -t sotera/ubuntu-cudnn4:1 .
docker build -f ubuntu-cudnn4-caffeprep.docker -t sotera/ubuntu-cudnn4-caffeprep:1 .
docker build -f ubuntu-cudnn4-nlpcaffe.docker -t sotera/ubuntu-cudnn4-nlpcaffe:1 .

docker login

docker push sotera/ubuntu-cudnn4:1
docker push sotera/ubuntu-cudnn4-caffeprep:1
docker push sotera/ubuntu-cudnn4-nlpcaffe:1



