from deep_translator import GoogleTranslator as T
import threading
import queue


class Translator(threading.Thread):
    """
    Classe para traduzir textos usando Google Translate.
    Herda de threading.Thread para permitir execução assíncrona.
    """

    def __init__(self, speaker=None, src_lang="pt", dest_lang="en"):
        super().__init__(daemon=True)  # Define a thread como daemon
        self.queue = queue.Queue()  # Fila para armazenar textos a serem traduzidos
        self.speaker = speaker
        # Inicia a thread
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.start()

    def run(self):
        """
        Método que executa a thread para traduzir os textos na fila.
        """
        self.translator = T(source=self.src_lang, target=self.dest_lang)
        print("Thread de tradução iniciada")
        while True:
            text = self.queue.get()
            translated_text = self.translator.translate(text)
            self.speaker.add_to_speak(translated_text) if self.speaker else None
            print(f"\nTexto: {text} \nTexto traduzido: {translated_text}\n")

    def add_to_translate(self, text):
        """
        Adiciona um texto à fila para ser traduzido.

        Args:
            text (str): O texto a ser adicionado à fila.
        """
        self.queue.put(text)
