#!/bin/bash 
printf "Cloning Coqui AI TTS repository...\n"
git clone https://github.com/coqui-ai/TTS TTS_repo
cd TTS_repo  
git checkout e9e0784

printf "Installing pre-requisite packages...\n"
pip install -r requirements.txt
python setup.py develop
cd ..

mkdir models
cd models 
printf "Downloading models into models/ directory ...\n"
wget https://www.dropbox.com/s/kf2kydzkri6tkk7/checkpoint_100000.pth.tar
gdown --id 1X09hHAyAJOnrplCUMAdW_t341Kor4YR4 -O vocoder_model.pth.tar

cd ..
uvicorn main:app --reload