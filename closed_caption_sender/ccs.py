# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import datetime as dt
import queue
import threading

bad_words = (
    open("closed_caption_sender/bad_words.txt", "r", encoding="utf-8")
    .read()
    .splitlines()
)


def exclued_bad_words(text):
    for word in bad_words:
        # text = text.replace(" " + word + " ", " " + "*" * len(word) + " ")
        text = text.replace(" " + word + " ", " * ")

    return text


class ClosedCaptionSender(threading.Thread):
    def __init__(self, caption_url):
        super().__init__(daemon=True)  # Define a thread como daemon
        self.caption_url = caption_url
        self.queue = queue.Queue()
        self.start()
        self.sec = 1

    def run(self):
        """
        Método que executa a thread para enviar as legendas na fila.
        """
        print("Thread de envio de legendas iniciada")
        while True:
            text = self.queue.get()
            self.send_caption(text)

    def send_caption(self, text):
        timestamp = datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")[
            :-6
        ]
        caption_text = f"{timestamp}\n{text}\n"

        headers = {"Content-Type": "text/plain"}

        response = requests.post(
            self.caption_url + "&seq=%d" % self.sec,
            data=caption_text.encode("utf-8"),
            headers=headers,
        )

        print(self.caption_url + "&seq=%d" % self.sec)
        print(f"Enviando legenda: {caption_text}")
        self.sec += 1

        if response.status_code == 200:
            print("Legenda enviada com sucesso!")
        else:
            print(f"Erro ao enviar legenda: {response.status_code} - {response.text}")

    def add_to_send(self, text):
        """
        Adiciona um texto à fila para ser enviado como legenda.

        Args:
            text (str): O texto a ser adicionado à fila.
        """
        self.queue.put(text)


class ClosedCaptionSenderToFile(threading.Thread):
    def __init__(
        self, file_path, mode="a", upper=False, send_timestamp=True, limit=1000
    ):
        super().__init__(daemon=True)  # Define a thread como daemon
        self.file_path = file_path
        self.mode = mode
        self.upper = upper
        self.send_timestamp = send_timestamp
        self.queue = queue.Queue()
        self.start()
        self.limit = limit
        self.step = 10

    def run(self):
        """
        Método que executa a thread para enviar as legendas na fila.
        """
        print("Thread de envio de legendas iniciada")
        while True:
            text = self.queue.get()
            self.send_caption(text)

    def send_caption(self, text):
        timestamp = datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")[
            :-6
        ]

        if len(text) > self.limit:

            words = text.split()
            while len(text) > self.limit and len(words) > self.step:
                text = " ".join(words[self.step : -1])
                words = text.split()
                if len(text) <= self.limit:
                    break

        if self.send_timestamp:
            caption_text = f"{timestamp}\n{text}\n"
        else:
            caption_text = f"{text}\n"

        if self.upper:
            caption_text = caption_text.upper()

        print(caption_text, end="\r")

        with open(self.file_path, self.mode, encoding="utf-8") as f:
            f.write(caption_text)

    def add_to_send(self, text):
        """
        Adiciona um texto à fila para ser enviado como legenda.

        Args:
            text (str): O texto a ser adicionado à fila.
        """
        self.queue.put(exclued_bad_words(text))
        print(text)
