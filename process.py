from tts_handler import TTSHandler
import sys 

handler = TTSHandler()

if __name__ == "__main__":
    message = sys.argv[1]
    print("Synthesizing message: {} ...\n".format(message))
    handler.synthesize(message) 