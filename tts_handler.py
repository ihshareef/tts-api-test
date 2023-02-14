from core import CoreTTS
from utils.helpers import separate_text
import numpy as np
import os
# import scipy as sp
import uuid
import wave

sample_rate = 22050

class TTSHandler:
    def __init__(self):
        self.engine = CoreTTS()
        self.waveforms = []

    def synthesize(self, message: str):
        text_queue = separate_text(message)
        waveforms = []
        filenames = []
        for text in text_queue:
            filename = "{}.wav".format(str(uuid.uuid4()))
            self.engine.tts(text, filename)
            filenames.append(filename)
        self._get_concatenated_wav(filenames)       
        
    def _clear_files(self, filenames):
        for filename in filenames: 
            os.remove(filename)
            
    def _get_concatenated_wav(self, filenames, outfile_path="output_audio.wav"):
        data = [] 
        for infile in filenames:
            w = wave.open(infile, 'rb')
            data.append([w.getparams(), w.readframes(w.getnframes())])
            w.close()
        output = wave.open(outfile_path, 'wb')
        output.setparams(data[0][0])
        for i in range(len(data)):
            output.writeframes(data[i][1])
        output.close()
        self._clear_files(filenames)
            
