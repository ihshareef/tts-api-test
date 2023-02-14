import torch 
import sys

sys.path.append('TTS_repo')

from TTS_repo.TTS.tts.utils.generic_utils import setup_model
from TTS_repo.TTS.utils.io import load_config
from TTS_repo.TTS.tts.utils.text.symbols import symbols, phonemes
from TTS_repo.TTS.utils.audio import AudioProcessor
from TTS_repo.TTS.tts.utils.synthesis import synthesis
from TTS_repo.TTS.vocoder.utils.generic_utils import setup_generator
import numpy as np
import scipy as sp


class CoreTTS:
    def __init__(self, use_cuda = True):
        self.use_cuda = use_cuda
        # model paths
        TTS_MODEL = "models/checkpoint_100000.pth.tar"
        TTS_CONFIG = "models/config.json"
        VOCODER_MODEL = "models/vocoder_model.pth.tar"
        VOCODER_CONFIG = "models/config_vocoder.json"

        # load configs
        self.TTS_CONFIG = load_config(TTS_CONFIG)
        self.VOCODER_CONFIG = load_config(VOCODER_CONFIG)
        self.VOCODER_CONFIG.audio['stats_path'] = 'models/scale_stats.npy'
        
        # ap 
        self.ap = AudioProcessor(self.TTS_CONFIG.audio)
        self.ap_vocoder = AudioProcessor(self.VOCODER_CONFIG['audio'])
        self.scale_factor = [1,  self.VOCODER_CONFIG['audio']['sample_rate'] / self.ap.sample_rate]
        
        # LOAD TTS MODEL
        # multi speaker 
        speaker_id = None
        
        # load the model
        num_chars = len(phonemes) if self.TTS_CONFIG.use_phonemes else len(symbols)
        self.model = setup_model(num_chars, len([]), TTS_CONFIG)
        # load model state
        self.cp =  torch.load(TTS_MODEL, map_location=torch.device('cpu'))
        # load the model
        self.model.load_state_dict(self.cp['model'])
        if self.use_cuda:
            self.model.cuda()
        self.model.eval()
        
        # set model stepsize
        if 'r' in self.cp:
            self.model.decoder.set_r(self.cp['r'])
            
        # LOAD VOCODER MODEL
        self.vocoder_model = setup_generator(self.VOCODER_CONFIG)
        self.vocoder_model.load_state_dict(torch.load(self.VOCODER_MODEL, map_location="cpu")["model"])
        self.vocoder_model.remove_weight_norm()
        self.vocoder_model.inference_padding = 0
        
        if use_cuda:
            self.vocoder_model.cuda()
        self.vocoder_model.eval()
        
    def interpolate_vocoder_input(self, scale_factor, spec):
        """Interpolation to tolarate the sampling rate difference
        btw tts model and vocoder"""
        spec = torch.tensor(spec).unsqueeze(0).unsqueeze(0)
        spec = torch.nn.functional.interpolate(spec, scale_factor=scale_factor, mode='bilinear').squeeze(0)
        return spec


    def tts(self, text, output_path=None, figures=True):
        waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(self.model, text, self.TTS_CONFIG, self.use_cuda, self.ap, None, style_wav=None,
                                                                             truncated=False, enable_eos_bos_chars=self.TTS_CONFIG.enable_eos_bos_chars)
        mel_postnet_spec = self.ap.denormalize(mel_postnet_spec.T).T
        target_sr = self.VOCODER_CONFIG.audio['sample_rate']
        vocoder_input = self.ap_vocoder.normalize(mel_postnet_spec.T)
        # vocoder_input = mel_postnet_spec.T
        if self.scale_factor[1] != 1:
            vocoder_input = self.interpolate_vocoder_input(self.scale_factor, vocoder_input)
        else:
            vocoder_input = torch.tensor(vocoder_input).unsqueeze(0)
            waveform = self.vocoder_model.inference(vocoder_input)
        if self.use_cuda:
            waveform = waveform.cpu()
            waveform = waveform.numpy()
        
        waveform = waveform.squeeze()
    
        rate=self.VOCODER_CONFIG.audio['sample_rate']
        if output_path is not None:
            sp.io.wavfile.write(output_path + ".wav", rate, waveform)
        return alignment, mel_postnet_spec, stop_tokens, waveform