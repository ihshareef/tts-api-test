import onnxruntime as rt
import numpy as np
import simpleaudio as sa
import time
import os
import sys
from utils.ljspeech import LJSpeechProcessor
# 22,050 Hz
BITRATE = 22050

# Helper
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
   # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TtsSpeaker():
    def __init__(self):
        self.fs2_model = resource_path("..//..//models//fs2_model.onnx")
        self.mb_model = resource_path("..//..//models//mb_melgan_model.onnx")
        # Default variables for FastSpeech2
        self.speaker_ids = np.asarray((0))
        self.speaker_ids = np.asarray((0)).reshape((1))
        self.speed_ratios = np.asarray((1.0)).reshape((1))
        self.f0_ratios = np.asarray((1.0)).reshape((1))
        self.energy_ratios = np.asarray((1.0)).reshape((1))
        # processor
        self.processor = LJSpeechProcessor(data_dir=None, loaded_mapper_path=resource_path("..//..//conf//ljspeech_mapper.json"))
        self.play_obj = None
        self.is_dv_playing = False

    def speak(self, input = None):
        if self.play_obj is not None:
            if self.play_obj.is_playing():
                self.play_obj.stop()
        self.is_playing = True
        # Replace with dynamic data
        input_ids = self.processor.text_to_sequence(input)
        input_length = len(input_ids)

        input_ids = np.asarray(input_ids)
        input_ids = input_ids.reshape((1, input_length))

        start = time.time()
        audios = self.convert_text_to_audio(input_ids)
        end = time.time()
        print("Difference: {diff}".format(diff=end-start))
        self.play_obj = sa.play_buffer(audios, 1, 4, BITRATE)

        # wait for playback to finish before exiting
        self.play_obj.wait_done()
        self.is_dv_playing = False
        return True

    # Wrapper for simpleaudio's stop_all function
    def interrupt(self):
        sa.stop_all()

    def convert_text_to_audio(self, input):
        sess_options = rt.SessionOptions()
        sess_options.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
        start = time.time()
        sess = rt.InferenceSession(self.fs2_model,
                           providers=rt.get_available_providers(),
                           sess_options=sess_options)
        mel_before, mel_outputs, duration_outputs, _, _ = sess.run(None, {
            sess.get_inputs()[0].name: self.energy_ratios.astype(np.float32),
            sess.get_inputs()[1].name: self.f0_ratios.astype(np.float32),
            sess.get_inputs()[2].name: input.astype(np.int32),
            sess.get_inputs()[3].name: self.speaker_ids.astype(np.int32),
            sess.get_inputs()[4].name: self.speed_ratios.astype(np.float32),
        })
        end = time.time()

        start_1 = time.time()
        sess_vocoder = rt.InferenceSession(self.mb_model,
                           providers=rt.get_available_providers(),
                           sess_options=sess_options)
        audios = sess_vocoder.run(None, { sess_vocoder.get_inputs()[0].name: mel_outputs.astype(np.float32)})
        end_1 = time.time()

        print("fs2-diff: Diff {diff}".format(diff=end-start))
        print("vocoder-diff:Diff {diff}".format(diff=end_1-start_1))

        return np.asarray(audios)[0][0, :, 0]