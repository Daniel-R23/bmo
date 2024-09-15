import tkinter as tk
import speech_recognition as sr
from openai import OpenAI
import pyttsx3
from playsound import playsound
from PIL import Image, ImageTk
import os
# Configuração da API do ChatGPT
api_key = os.getenv("OPENAI_API_KEY")

engine = pyttsx3.init()

# Variável global para controlar o estado do microfone
microphone_active = False

# Funções para tocar sons
def play_start_sound():
    playsound(sound="start_listening.wav")

# def play_end_sound():
    # playsound(sound="stop_listening.wav")


# Função para fazer a requisição para o ChatGPT
def chatgpt_request(prompt):
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


# Função para iniciar o reconhecimento de voz
def recognize_speech():

    start_listening_visual()
    # play_start_sound()

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Ajustando para o ruído ambiente...")
        recognizer.adjust_for_ambient_noise(source)
        update_text("Diga algo!")
        audio = recognizer.listen(source)

    stop_listening_visual()
    # play_end_sound()

    try:
        update_text("Reconhecendo...")
        text = recognizer.recognize_google(audio, language="pt-BR")
        update_text(text)
        # Fazendo requisição para o ChatGPT
        response = chatgpt_request(text)
        update_text(response)
        speak_text(response)
    except sr.UnknownValueError:
        update_text("Não foi possível entender o que foi dito.")
        speak_text("Não foi possível entender o que foi dito.")
    except sr.RequestError as e:
        update_text(f"Erro na requisição; {e}")
        speak_text("Erro na requisição")

    # Continuar escutando
    window.after(100, recognize_speech)


# Função para falar o texto
def speak_text(text):
    engine.say(text=text)
    engine.runAndWait()

# Função para ajustar o tamanho da fonte dinamicamente
def adjust_font_size(label, text, max_font_size=18, min_font_size=8):
    font_size = max_font_size
    label.config(font=("Arial", font_size, "bold"),fg="black", text=text, wraplength=460)
    label.update_idletasks()

    while label.winfo_reqwidth() > label.winfo_width() or label.winfo_reqheight() > label.winfo_height():
        font_size -= 1
        if font_size < min_font_size:
            break
        label.config(font=("Arial", font_size, "bold"), fg="black", wraplength=460)
        label.update_idletasks()


# Função para atualizar o texto na interface
def update_text(new_text):
    adjust_font_size(output_label, new_text)


# Função para iniciar o efeito visual de escuta
def start_listening_visual():
    hide_image_and_show_text()
    window.configure(bg="#72cbb7")  # Troca fundo para azul escuro
    output_label.config(bg="#72cbb7")

# Função para parar o efeito visual de escuta
def stop_listening_visual():
    window.configure(bg="#7ac99a")  # Volta fundo para verde
    output_label.config(bg="#7ac99a")


# Função para lidar com o clique na tela
def on_screen_click(event=None):
    global microphone_active
    if microphone_active:
        microphone_active = False
        stop_listening_visual()
        show_image()
    else:
        microphone_active = True
        start_listening_visual()
        recognize_speech()


# Função para carregar e exibir a imagem no modo stand-by
def show_image():
    image = Image.open("bmo01.jpg")  # Insira o caminho da imagem
    image = image.resize((480, 320))  # Redimensiona para o tamanho da tela
    photo = ImageTk.PhotoImage(image)

    # Exibe a imagem
    background_label.config(image=photo)
    background_label.image = photo  # Manter referência para evitar garbage collection
    output_label.pack_forget()  # Esconde o label de texto


# Função para remover a imagem e mostrar o texto ao entrar no modo de escuta
def hide_image_and_show_text():
    background_label.config(image="")  # Remove a imagem
    background_label.pack_forget()
    output_label.pack(expand=True)  # Mostra o label de texto




# Configuração da interface gráfica com Tkinter
window = tk.Tk()
window.title("ChatGPT Voice Interface")
window.geometry("480x320")  # Tamanho da tela de 3.5" polegadas

# Adiciona o label para a imagem de fundo
background_label = tk.Label(window)
background_label.pack(fill="both", expand=True)

# Label para exibir o texto
output_label = tk.Label(window, text="...", font=("Arial", 80, "bold"), fg="white", bg="#072616")

# Mostra a imagem no início (modo stand-by)
show_image()

# Adiciona o evento de clique na tela
window.bind("<Button-1>", on_screen_click)

# Executar a interface
window.mainloop()
