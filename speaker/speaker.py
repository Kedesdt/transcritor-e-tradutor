import pyttsx3
import threading
import queue
import time


class Speaker(threading.Thread):
    """
    Classe para falar um texto em português usando pyttsx3.
    Herda de threading.Thread para permitir execução assíncrona.
    """

    def __init__(self, voice="brazil", rate=150):

        super().__init__(
            daemon=True
        )  # Define a thread como daemon para não bloquear o encerramento do programa
        self.queue = queue.Queue()  # Fila para armazenar textos a serem falados
        self.voice = voice
        self.rate = rate
        self.start()

    def run(self):
        """
        Método que executa a thread para falar os textos na fila.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("voice", self.voice)
        self.engine.setProperty("rate", self.rate)
        print("Thread de fala iniciada")
        while True:
            text = self.queue.get()
            self.say(text)
            self.engine.runAndWait()

    def say(self, text):
        """
        Função para falar um texto em português usando pyttsx3.

        Args:
            text (str): O texto a ser falado.

        """
        # print(text)
        self.engine.say(text)

    def add_to_speak(self, text):
        """
        Adiciona um texto à fila para ser falado.

        Args:
            text (str): O texto a ser adicionado à fila.
        """
        self.queue.put(text)

    def list_voices(self):
        """
        Lista as vozes disponíveis no pyttsx3.
        """
        voices = self.engine.getProperty("voices")
        for voice in voices:
            print(f"ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")
