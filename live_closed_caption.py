from translator.translator import Translator
from vosk_transcriber.vosk_transcriber import VoskTranscriber
from speaker.speaker import Speaker
from closed_caption_sender.ccs import ClosedCaptionSender
import threading
import queue
import sys
import sounddevice as sd

q = queue.Queue()


def callback(text):

    q.put(text)


def send_and_print(ccs):
    while True:
        if q.qsize() > 1:
            text = q.get()
            while not q.empty():
                text += " " + q.get()
            ccs.add_to_send(text)
            # print(f"Enviando legenda: {text}")
            # print(text, end=" ", flush=True)


def cc(
    caption_url="http://upload.youtube.com/closedcaption?cid=th4m-j4zm-akqc-8h62-eac8",
    device=0,
):

    ccs = ClosedCaptionSender(caption_url=caption_url)
    transcriber = VoskTranscriber(translator=None, speaker=None, callback=None)
    threading.Thread(target=send_and_print, args=(ccs,), daemon=True).start()
    transcriber.real_time_transcribe_partial(callback=callback, device=device)


def main():
    if len(sys.argv) > 1:
        caption_url = sys.argv[1]
    else:
        caption_url = None

    if len(sys.argv) > 2:
        device = sys.argv[2]
    else:
        device = None

    caption_url = caption_url if caption_url else input("Enter caption URL: ")
    print("\nAvailable devices:")
    devices = sd.query_devices(kind="input")
    if type(devices) is not list:
        devices = [devices]
    for i, device_info in enumerate(devices):
        print(f"{i}: {device_info['name']}")

    device = int(device) if device is not None else int(input("Enter device number: "))

    cc(caption_url=caption_url, device=device)


if __name__ == "__main__":
    main()
