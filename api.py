from fastapi import FastAPI
from synthesizers.Synthesizer import Synthesizer
from pydantic import BaseModel
from utils.helpers import separate_text
import numpy as np
from scipy.io.wavfile import write

# app = FastAPI()

sample_rate = 22050
n_channels = 1

# initialize synthesizer
synthesizer = Synthesizer()
text = "މިއީ ދިވެހި ބަހުގެ މިސާލެކެވެ. މިއީ ރީތި ޖުމްލައެކެވެ."
wavform = synthesizer.speak(text)
write("output.wav", sample_rate, wavform)

# class SynthesisRequest(BaseModel):
#     message: str
#     callback: str

# @app.get("/synthesize")
# def synthesize(request: SynthesisRequest):
#     text_queue = separate_text(request.message)
#     waveforms = []
#     for text in text_queue:
#         waveforms.append(synthesizer.speak(text))
#     output_waveform = np.concatenate(waveforms)
#     write("output.wav", sample_rate, output_waveform)


