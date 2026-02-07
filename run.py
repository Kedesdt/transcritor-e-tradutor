import json
from translator.translator import Translator
from vosk_transcriber.vosk_transcriber import VoskTranscriber
from speaker.speaker import Speaker
from closed_caption_sender.ccs import ClosedCaptionSender, ClosedCaptionSenderToFile
import threading
import queue

q = queue.Queue()


def callback(text):

    q.put(text)


def send_and_print(ccs):
    while True:
        if not q.empty():
            text = q.get()
            while not q.empty():
                text += " " + q.get()
            ccs.add_to_send(text)
            # print(f"Enviando legenda: {text}")
            # print(text, end=" ", flush=True)


def cc():

    ccs = ClosedCaptionSender(
        caption_url="http://upload.youtube.com/closedcaption?cid=th4m-j4zm-akqc-8h62-eac8"
    )
    transcriber = VoskTranscriber(translator=None, speaker=None, callback=None)
    threading.Thread(target=send_and_print, args=(ccs,), daemon=True).start()
    transcriber.real_time_transcribe_partial(callback=callback)


def cc_to_file():

    ccs = ClosedCaptionSenderToFile(
        file_path=config["file_path"],
        mode="w",
        upper=True,
        send_timestamp=False,
        limit=20 * 7,
    )
    # translator = Translator(speaker=None, src_lang="pt", dest_lang="en")
    transcriber = VoskTranscriber(
        translator=None, speaker=None, callback=ccs.add_to_send
    )
    transcriber.real_time_transcribe_partial_2()
    # transcriber.real_time_transcribe()


def main():
    speaker = Speaker(
        voice="HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
    )
    translator = Translator(speaker=speaker, src_lang="pt", dest_lang="en")
    ccs = ClosedCaptionSender(
        caption_url="http://upload.youtube.com/closedcaption?cid=th4m-j4zm-akqc-8h62-eac8"
    )
    transcriber = VoskTranscriber(
        translator=translator, speaker=speaker, callback=ccs.add_to_send
    )

    # Inicia a transcrição em tempo real
    # transcriber.file_transcribe(
    #    file_path="C:\\Users\\kdtorres\\Downloads\\audio_16_mono.wav"
    # )
    transcriber.real_time_transcribe()


config = json.loads(open("config.json", "r", encoding="utf-8").read())
print(config)
if __name__ == "__main__":
    # cc()
    cc_to_file()
