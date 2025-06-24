from translator.translator import Translator
from vosk_transcriber.vosk_transcriber import VoskTranscriber
from speaker.speaker import Speaker


def main():
    speaker = Speaker(
        voice="HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
    )
    translator = Translator(speaker=speaker, src_lang="pt", dest_lang="en")
    transcriber = VoskTranscriber(translator=translator, speaker=speaker)

    # Inicia a transcrição em tempo real
    # transcriber.file_transcribe(
    #    file_path="C:\\Users\\kdtorres\\Downloads\\audio_16_mono.wav"
    # )
    transcriber.real_time_transcribe()


if __name__ == "__main__":
    main()
