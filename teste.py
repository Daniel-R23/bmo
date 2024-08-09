from openai import OpenAI
import pyttsx3



class ConfigManager:
    def __init__(self):
        self.openai_api_key = "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"

class OpenAiChatBot:
    def __init__(self, config_manager):
        self.openai = OpenAI(api_key=config_manager.openai_api_key)
        self.default_prompt = "Você é um assistente muito prestativo e criativo que dá respostas curtas e diretas, sempre fala números por extenso"
    
    def get_response(self, user_message):
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content": self.default_prompt},
                {"role":"user", "content": user_message}
            ]
        )
        print("Resposta: " + response.choices[0].message.content)
        return response.choices[0].message.content

class MainApplication:
    def __init__(self):
        self.config = ConfigManager()
        self.chatbot = OpenAiChatBot(self.config)
        self.tts_engine = pyttsx3.init()

    def run(self):
        user_message = "Oi"
        response = self.chatbot.get_response(user_message)
        self.tts_engine.say(response)
        self.tts_engine.runAndWait()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
        