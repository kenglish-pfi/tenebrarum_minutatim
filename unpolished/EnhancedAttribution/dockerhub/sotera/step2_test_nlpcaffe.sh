#!/bin/bash
docker run -it sotera/ubuntu-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; ./data/language_model/get_lm.sh'
docker run -it sotera/ubuntu-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; python ./examples/language_model/create_lm.py --make_data'
docker run -it sotera/ubuntu-cudnn4-nlpcaffe:1  /bin/bash -c 'cd /home/caffe-user/nlpcaffe ; ./examples/language_model/train_lm.sh'




