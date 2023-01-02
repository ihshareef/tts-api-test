import os
import sys
import torch
import time

from .TTS.TTS.tts.utils.generic_utils import setup_model
from .TTS.TTS.utils.io import load_config
from .TTS.TTS.tts.utils.text.symbols import symbols, phonemes
from .TTS.TTS.utils.audio import AudioProcessor
from .TTS.TTS.tts.utils.synthesis import synthesis
from .TTS.TTS.vocoder.utils.generic_utils import setup_generator
from utils.ljspeech import LJSpeechProcessor

# model paths
TTS_MODEL = "./models/checkpoint_100000.pth.tar"
TTS_CONFIG = "./models/config.json"
VOCODER_MODEL = "./models/vocoder_model.pth.tar"
VOCODER_CONFIG = "./models/config_vocoder.json"

# load configs
TTS_CONFIG = load_config(TTS_CONFIG)
VOCODER_CONFIG = load_config(VOCODER_CONFIG)
VOCODER_CONFIG.audio['stats_path'] = './models/scale_stats.npy'


class Synthesizer:

    def __init__(self):
        self.vocoder_model = setup_generator(VOCODER_CONFIG)
        self.vocoder_model.load_state_dict(torch.load(VOCODER_MODEL, map_location="cpu")["model"])
        self.processor = LJSpeechProcessor(data_dir=None,
                                           loaded_mapper_path='./conf/ljspeech_mapper.json')
        self.vocoder_model.remove_weight_norm()
        self.vocoder_model.inference_padding = 0
        # load the audio processor
        self.ap = AudioProcessor(**TTS_CONFIG.audio)
        self.ap_vocoder = AudioProcessor(**VOCODER_CONFIG['audio'])

        self.cp = torch.load(TTS_MODEL, map_location=torch.device('cpu'))
        num_chars = len(phonemes) if TTS_CONFIG.use_phonemes else len(symbols)
        speakers = []
        self.model = setup_model(num_chars, len(speakers), TTS_CONFIG)
        # load model state
        cp = torch.load(TTS_MODEL, map_location=torch.device('cpu'))
        self.use_cuda = False

        # load the model
        self.model.load_state_dict(cp['model'])
        if 'r' in cp:
            self.model.decoder.set_r(cp['r'])

        # scale factor for sampling rate difference
        self.scale_factor = [1, VOCODER_CONFIG['audio']['sample_rate'] / self.ap.sample_rate]
        print(f"scale_factor: {self.scale_factor}")

    def _interpolate_vocoder_input(self, scale_factor, spec):
        """Interpolation to tolarate the sampling rate difference
        btw tts model and vocoder"""
        spec = torch.tensor(spec).unsqueeze(0).unsqueeze(0)
        spec = torch.nn.functional.interpolate(spec, scale_factor=scale_factor, mode='bilinear').squeeze(0)
        return spec

    def _tts(self, text, figures=True):
        use_gl = False
        enable_eos_bos_chars = TTS_CONFIG.enable_eos_bos_chars
        waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(self.model, text, TTS_CONFIG, self.use_cuda,
                                                                                         self.ap, None, style_wav=None,
                                                                                         truncated=False,
                                                                                         enable_eos_bos_chars=enable_eos_bos_chars)
        mel_postnet_spec = self.ap.denormalize(mel_postnet_spec.T).T
        if not use_gl:
            target_sr = VOCODER_CONFIG.audio['sample_rate']
            vocoder_input = self.ap_vocoder.normalize(mel_postnet_spec.T)
            if self.scale_factor[1] != 1:
                vocoder_input = self.interpolate_vocoder_input(self.scale_factor, vocoder_input)
            else:
                vocoder_input = torch.tensor(vocoder_input).unsqueeze(0)
            waveform = self.vocoder_model.inference(vocoder_input)
        if self.use_cuda and not use_gl:
            waveform = waveform.cpu()
        if not use_gl:
            waveform = waveform.numpy()
        waveform = waveform.squeeze()
        rate = VOCODER_CONFIG.audio['sample_rate']

        return alignment, mel_postnet_spec, stop_tokens, waveform

    def speak(self, text: str):
        _,_,_,waveform = self._tts(text)
        return waveform
