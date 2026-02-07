import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import wave
import numpy as np
import os
from speaker.speaker import Speaker
from translator.translator import Translator

modelpath = "C:\\Users\\kdtorres\\Documents\\Programacao\\transcritor_vosk\\vosk-model-small-pt-0.3"
modelpath = "C:\\Users\\kdtorres\\Documents\\Programacao\\transcritor_vosk\\vosk-model-pt-fb-v0.1.1-pruned"
# modelpath = "C:\\Users\\kdtorres\\Documents\\Programacao\\transcritor_vosk\\vosk-model-pt-fb-v0.1.1-20220516_2113"
# modelpath = "C:\\Users\\kdtorres\\Documents\\Programacao\\transcritor_vosk\\vosk-model-pt-fb-v0.1.1"


class VoskTranscriber:
    """
    Classe para transcrever áudio em texto usando o Vosk.
    """

    def __init__(
        self,
        model_path=modelpath,
        translator: Translator = None,
        speaker: Speaker = None,
        callback=None,
    ):
        self.model_path = model_path
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo Vosk não encontrado em {model_path}")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.queue = queue.Queue()
        self.translator = translator
        self.speaker = speaker
        self.callback = callback

    def real_time_transcribe(self):

        def callback(indata, frames, time, status):
            self.queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            print("Fale algo...")
            while True:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    # print(json.loads(self.recognizer.Result())["text"])
                    result = json.loads(self.recognizer.Result())["text"]
                    if self.translator:
                        (
                            self.translator.add_to_translate(result, self.callback)
                            if self.translator
                            else (
                                self.speaker.add_to_speak(result)
                                if self.speaker
                                else None
                            )
                        )
                    elif self.callback:
                        self.callback(result)

    def real_time_transcribe_partial(self, callback=None, device=None):

        def callback_func(indata, frames, time, status):
            self.queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback_func,
            device=device,
        ):
            index = 0

            print("Fale algo...")
            while True:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    # print(json.loads(self.recognizer.Result())["text"])
                    result = json.loads(self.recognizer.Result())["text"]
                    w = result.split()
                    for word in w[index:]:
                        if callback:
                            callback(word)
                        elif self.callback:
                            self.callback(word)

                    index = 0

                else:
                    partial = json.loads(self.recognizer.PartialResult())["partial"]
                    if partial:
                        w = partial.split()
                        if index < len(w) - 2:

                            for word in w[index : len(w) - 2]:
                                if callback:
                                    callback(word)
                                elif self.callback:
                                    self.callback(word)
                            index = len(w) - 2

    def real_time_transcribe_partial_2(self, callback=None, device=None):

        def callback_func(indata, frames, time, status):
            self.queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback_func,
            device=device,
        ):
            index = 0

            print("Fale algo...")

            text = ""
            while True:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    # print(json.loads(self.recognizer.Result())["text"])
                    result = json.loads(self.recognizer.Result())["text"]
                    text = result
                    index = 0

                else:
                    partial = json.loads(self.recognizer.PartialResult())["partial"]

                    if partial:
                        w = partial.split()
                        if index < len(w) - 2:

                            for word in w[index : len(w) - 2]:
                                text += " " + word
                            index = len(w) - 2

                if callback:
                    callback(text)
                elif self.callback:
                    self.callback(text)

    def file_transcribe(self, file_path, speaker: Speaker = None):
        self.wf = wave.open(file_path, "rb")
        self.model = Model(modelpath)
        self.reccognizer = KaldiRecognizer(self.model, self.wf.getframerate())

        output = ["", ""]

        def callback(outdata, frames, time, status):
            data = self.wf.readframes(frames)
            if len(data) == 0:
                raise sd.CallbackStop()
            # Converta os bytes para um array NumPy do tipo correto
            audio_array = np.frombuffer(data, dtype="int16")
            # Ajuste o shape para canais (mono ou estéreo)
            audio_array = audio_array.reshape(-1, self.wf.getnchannels())
            if self.translator is None and self.speaker is None:
                outdata[: len(audio_array)] = audio_array
            if self.reccognizer.AcceptWaveform(data):
                # print(json.loads(rec.Result())["text"], flush=True)
                result = json.loads(self.reccognizer.Result())["text"]
                output[0] += result + " "
                (
                    self.translator.add_to_translate(result)
                    if self.translator
                    else speaker.add_to_speak(result) if speaker else None
                )
            else:
                output[1] = json.loads(self.reccognizer.PartialResult())["partial"]
                """if output[1] != "":
                    os.system("cls" if os.name == "nt" else "clear")
                    for partial in output:
                        if partial != "":
                            print(partial, flush=True, end=" ")"""

        with sd.OutputStream(
            samplerate=self.wf.getframerate(),
            channels=self.wf.getnchannels(),
            dtype="int16",
            callback=callback,
            blocksize=4000,
        ):
            print("Reproduzindo e transcrevendo...")
            sd.sleep(int(self.wf.getnframes() / self.wf.getframerate() * 1000))
        print(json.loads(self.reccognizer.FinalResult())["text"])


def real_time_transcribe():
    print("Transcrição em tempo real iniciando. Aguarde....")
    model = Model(modelpath)
    rec = KaldiRecognizer(model, 16000)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback
    ):
        print("Fale algo...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(json.loads(rec.Result())["text"])


def file_transcribe(file_path, speaker: Speaker = None):
    wf = wave.open(file_path, "rb")
    model = Model(modelpath)
    rec = KaldiRecognizer(model, wf.getframerate())

    output = ["", ""]

    def callback(outdata, frames, time, status):
        data = wf.readframes(frames)
        if len(data) == 0:
            raise sd.CallbackStop()
        # Converta os bytes para um array NumPy do tipo correto
        audio_array = np.frombuffer(data, dtype="int16")
        # Ajuste o shape para canais (mono ou estéreo)
        audio_array = audio_array.reshape(-1, wf.getnchannels())
        # outdata[: len(audio_array)] = audio_array
        if rec.AcceptWaveform(data):
            # print(json.loads(rec.Result())["text"], flush=True)
            result = json.loads(rec.Result())["text"]
            output[0] += result + " "
            speaker.add_to_speak(result) if speaker else None
        else:
            output[1] = json.loads(rec.PartialResult())["partial"]
            if output[1] != "":
                os.system("cls" if os.name == "nt" else "clear")
                for partial in output:
                    if partial != "":
                        print(partial, flush=True, end=" ")

    with sd.OutputStream(
        samplerate=wf.getframerate(),
        channels=wf.getnchannels(),
        dtype="int16",
        callback=callback,
        blocksize=4000,
    ):
        print("Reproduzindo e transcrevendo...")
        sd.sleep(int(wf.getnframes() / wf.getframerate() * 1000))
    print(json.loads(rec.FinalResult())["text"])
