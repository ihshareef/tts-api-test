from doctest import OutputChecker
from core import CoreTTS
from utils.helpers import separate_text
from utils.cleaners import dhivehi_cleaners
import numpy as np
import os
from scipy.io.wavfile import read, write
import uuid
import wave

sample_rate = 22050

class TTSHandler:
    def __init__(self):
        self.engine = CoreTTS()
        self.waveforms = []

    def synthesize(self, message: str) -> str:
        message = dhivehi_cleaners(message)
        text_queue = separate_text(message)
        filenames = []
        for text in text_queue:
            filename = "{}.wav".format(str(uuid.uuid4()))
            self.engine.tts(text, filename)
            filenames.append(filename)
        return self._get_concatenated_wav(filenames)       

            
    def _get_concatenated_wav(self, filenames):
        
        outfile_path = "file_{}.wav".format(str(uuid.uuid4()))
        concatenated_data = []
        sr = None
        for filename in filenames:
            filename = "{}".format(filename)
            sr, x = read(filename)
            concatenated_data.append(x)
        z = np.concatenate(tuple(concatenated_data))
        self._clear_files(filenames)
        
        write(outfile_path, sr, z)
        
        return outfile_path
            
        
    def _clear_files(self, filenames):
        for filename in filenames: 
            os.remove(filename)