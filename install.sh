pip install -r requirements.txt
mkdir -p models
cd models
wget https://www.dropbox.com/s/t51q81c5zdnfnk8/checkpoint_100000.pth.tar checkpoint_100000.pth.tar
wget https://www.dropbox.com/s/u5fl75qzhquyjze/config.json config.json
wget https://www.dropbox.com/s/fvzv8xmvew59eva/config_vocoder.json config_vocoder.json
wget https://www.dropbox.com/s/qr6h7u192cspi0w/scale_stats.npy scale_stats.npy
wget https://www.dropbox.com/s/suhh8bey6qvhr3a/vocoder_model.pth.tar vocoder_model.pth.tar
cd ../
cd synthesizers
git clone https://github.com/coqui-ai/TTS TTS
cd TTS
git checkout e9e0784
pip install -r requirements.txt
python setup.py develop
cd ../../
