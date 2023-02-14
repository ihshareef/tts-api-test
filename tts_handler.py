from core import CoreTTS
from utils.helpers import separate_text
import numpy as np
import scipy as sp

sample_rate = 22050

class TTSHandler:
    def __init__(self):
        self.engine = CoreTTS()
        self.waveforms = []
        
    def synthesize(self, message: str):
        text_queue = separate_text(message)        
        waveforms = [] 
        for text in text_queue:
            waveforms.append(self.engine.tts(text))
        output_waveform = np.concatenate(waveforms)
        # write a wavefile 
        sp.io.wavfile.write("output.wav", sample_rate, output_waveform)
            
    