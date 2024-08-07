from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings, play, save
from openai import OpenAI
import speech_recognition as sr
from os import listdir, path
import re
import cv2 as cv
import time
from threading import Thread
from pydub.utils import mediainfo
from pydub import AudioSegment
from pydub.playback import play

class ConfigManager:
    def __init__(self):
        self.openai_api_key = "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"
        self.elevenlabs_api_key = "7d5cfd8134920d29f16760c26492f2ef"

class SpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.activate_word = "Bimo"
        self.deactivate_word = "Desligar"

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Ouvindo...")
            try:
                play(AudioSegment.from_file("audio/beep_listen.mp3"))
                audio = self.recognizer.listen(source)
                return self.recognizer.recognize_google(audio, language="pt-BR")
            except sr.UnknownValueError:
                print("Não entendi, pode repetir...")
            except sr.RequestError as e:
                print(f"Erro de serviço; {e}")
    
    def is_activation_command(self, command):
        return re.search(r"\b[Bb]imo\b", command) is not None
    
    def is_deactivation_command(self, command):
        return command.lower() == self.deactivate_word
    
class OpenAiChatBot:
    def __init__(self, config_manager):
        self.openai = OpenAI(api_key=config_manager.openai_api_key)
        self.default_prompt = "Você é um assistente muito prestativo e criativo que dá respostas curtas e diretas, sempre fala números por extenso"
    
    def get_response(self, user_message):
        response = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system", "content": self.default_prompt},
                {"role":"user", "content": user_message}
            ]
        )
        print("Resposta: " + response.choices[0].message.content)
        return response.choices[0].message.content

class ElevenTTS:
    def __init__(self, config_manager, face_manager):
        self.tts = ElevenLabs(api_key=config_manager.elevenlabs_api_key)
        self.face = face_manager
        self.audio_path = "audio/audio.mp3"
    
    def response_speech(self, text):
        audio = self.tts.generate(
            text = text,
            voice = Voice(
                voice_id="upKpoeLp0kR7ycmLoGTI",
                settings=VoiceSettings(stability=0.5, similarity_boost=1.0, style=0.2, use_speaker_boost=False)
            ),
            model="eleven_multilingual_v2"
        )
        
        save(audio, self.audio_path)
        audio_info = mediainfo(self.audio_path)
        duration = float(audio_info.get('duration', 0))
        print(duration)
        
        t1 = Thread(target=play, args=(AudioSegment.from_file(self.audio_path),))
        # t1 = Thread(target=play, args=(audio,))
        #t2 = Thread(target=self.face.talk, args=(duration,))
        t1.start()
        #time.sleep(1)
        #t2.start()
        t1.join()
        #t2.join()


class FaceManager:
    def __init__(self):
        self.speak_path = path.dirname(path.realpath(__file__)) + "\\faces\\speak"
        self.idle_path = path.dirname(path.realpath(__file__)) + "\\faces"
        self.window_name = 'BMO'
        self.should_stop = False
        # cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        # cv.resizeWindow(self.window_name, 640, 480)

    def idle(self):
        video = cv.VideoCapture('faces/idle.mp4')
        if not video.isOpened():
            print("Erro ao abrir o vídeo")
            exit()
                
        while not self.should_stop:
            ret, frame = video.read()

            if not ret:
                video.set(cv.CAP_PROP_POS_FRAMES, 0)
                continue
                
                
            cv.imshow(self.window_name, frame)
            if cv.waitKey(25) & 0xFF == ord('q'):
                break

        video.release()
        #cv.destroyAllWindows()

    def talk(self, duration):
        start_time = time.time()
        while (time.time() - start_time) < duration:
            for img in listdir(self.speak_path):
                image = cv.imread(f'faces/speak/{img}')
                cv.imshow(self.window_name, image)
                cv.waitKey(60)  # Tempo de exibição em milissegundos
                if cv.waitKey(1) & 0xFF == 27:  # Pressione ESC para sair
                    break
        cv.destroyAllWindows()

class MainApplication:
    def __init__(self):
        self.config = ConfigManager()
        self.face = FaceManager()
        self.chatbot = OpenAiChatBot(self.config)
        self.tts = ElevenTTS(self.config, self.face)
        self.speech_recognition = SpeechRecognition()
        self.is_ativado = False

    def run(self):
        
        idleThread = Thread(target=self.face.idle)
        idleThread.start()

        while True:
            user_input = self.speech_recognition.listen()
            print(user_input)

            if user_input and self.speech_recognition.is_deactivation_command(user_input):
                print("Sistema desativado")
                self.tts.response_speech("Desligando")
                break
            if user_input and self.is_ativado:
                response = self.chatbot.get_response(user_input)
                self.tts.response_speech(response)
                

    def activate(self):
            idleThread = Thread(target=self.face.idle)
            idleThread.start()
            
            while True:
                user_input = self.speech_recognition.listen()
                print(user_input)

                if user_input and self.speech_recognition.is_activation_command(user_input):
                    print("Sistema ativado")
                    self.is_ativado = True
                    #self.face.should_stop = True
                    #idleThread.join()
                    #self.face.should_stop = False
                    audioThread = Thread(target=play, args=(AudioSegment.from_file("audio/saudacao1.mp3"),))
                    audioThread.start()
                    #self.face.talk(2)
                    audioThread.join()
                    self.run()
                    
                


def main():
    app = MainApplication()
    app.activate()
    
    #  config = ConfigManager()
    #   face = FaceManager()
    #   face.talk(5)
    #  tts = ElevenTTS(config, face)
    #  chat = OpenAiChatBot(config)
    #  resposta = chat.get_response("Me diga um ditado popular")
    #  tts.response_speech(resposta)
if __name__== "__main__":
    main()
