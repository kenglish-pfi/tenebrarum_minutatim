#!/bin/bash
docker run -it --device=/dev/nvidiactl --device=/dev/nvidia-uvm --device=/ddev/nvidia0 sotera/ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; ./data/language_model/get_lm.sh'
docker run -it --device=/dev/nvidiactl --device=/dev/nvidia-uvm --device=/ddev/nvidia0 sotera/ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; python ./examples/language_model/create_lm.py --make_data'
docker run -it --device=/dev/nvidiactl --device=/dev/nvidia-uvm --device=/ddev/nvidia0 sotera/ubuntu-nvidia367.57-cuda7.5-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; ./examples/language_model/train_lm.sh'




