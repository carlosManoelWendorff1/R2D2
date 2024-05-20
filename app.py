import datetime
import os
import requests
import json
import speech_recognition as sr
import pyttsx3
import webbrowser
from dotenv import load_dotenv

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


GOOGLE_API_KEY='AIzaSyBcihqJvQl6kXPhEWatU1zjYZbFMpmXz2Q'
model = genai.GenerativeModel('gemini-pro')
load_dotenv()
# Global variable to store the last text from gemini
lastText = ""

OPTIONS = ["\nIA",
           "\npesquisar na web",
           "\ncriar um lembrete",
           "\nprevisão do tempo",
           "\núltima resposta",
           "\nsair",
           "\ncancelar",
           "\npare",
           "\nconsulta anterior",
           "\npesquisa anterior",
           "\npesquisado antes",
           "\ngemini",
           "\ninteligência artificial",
           "\nnenhuma das opções anteriores"]


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    rate = 200
    engine.setProperty('voice',  'brazil')
    engine.setProperty('rate', rate-45)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)
        print("Ouvindo: ")
        microfone.pause_threshold = 1
        audio = microfone.listen(source)

    try:
        print("reconhecendo...")
        query = microfone.recognize_google(audio, language="pt-BR")
        print(f"usuário disse: {query}")

    except Exception as e:
        print("Poderia dizer novamente")
        return "none"

    return query

def search_web():
    speak("o que você gostaria de procurar?")
    query = recognize_speech()
    url = f"https://google.com/search?q={query}"
    webbrowser.open(url)
    speak(f"aqui está os resultados para {query}")

def set_reminder():
    speak("O que devo lembrá-lo?")
    task = recognize_speech()
    speak("em quantos minutos?")
    mins = recognize_speech()
    mins = int(mins)
    reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=mins)
    with open('reminder.txt', 'a') as f:
        f.write(f"{reminder_time} - {task}")
    speak(f"Lembrete definido para {mins} minutos a partir de agora.")


def gemini(lt):
    global lastText
    speak("o que você gostaria de pesquisar?")
    frase = recognize_speech()
    instructions = "Responda o seguinte texto, mantenha-se curto, no máximo 3 frases, em portugês:"
    text = instructions + frase

    if(len(lt) > 0):
        text += "\n Além disso leve em conta o texto anterior: "
        text += lt
    print(text)
    response = model.generate_content(text)
    print(response.text)
    speak(response.text)
    to_markdown(response.text)
    lastText = response.text
    with open('mensagem.txt', 'a') as f:
        f.write(f"{response}")

def weather():
    speak("Qual cidade você gostaria de saber o tempo?")
    query = recognize_speech()
    cidade = query
    chave_api = API_KEY_TEMP
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave_api}&units=metric"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        temperatura = dados["main"]["temp"]
        descricao = dados["weather"][0]["description"]
        speak(f"Em {cidade}, a temperatura atual é de {temperatura} graus Celsius e o tempo está {descricao}.")
    else:
        speak("Não foi possível obter os dados de tempo.")

def parseIaResponse(text):
    global lastText
    if "IA" in text or "gemini" in text or "inteligência artificial" in text:
        lastText = ""
        gemini(lastText)
        
    elif "pesquisar na web" in text:
        search_web()

    elif "criar um lembrete" in text:
        set_reminder()
    
    elif "previsão do tempo" in text:
        weather()

    elif "última resposta" in text or "consulta anterior" in text or "pesquisa anterior" in text or "pesquisado antes" in text:
        gemini(lastText)

    elif "pare" in text or "sair" in text or "cancelar" in text:
        speak("Até logo.")
        main()

    elif "nenhuma das opções anteriores" in text:
        speak("Desculpe, não entendi. Poderia repetir?")

    else:
        speak("Desculpe, não entendi. Poderia repetir?")

def talk():
    while True:
        query = recognize_speech()
        instructions = "\nSelecione uma das seguintes opções com base no texto que foi passado:"
        for o in OPTIONS:
            instructions += o
        text = query + instructions
        response = model.generate_content(text)
        print("opção selecioanada : " + response.text)
        if(query != None or query != "none"):
            parseIaResponse(response.text)


def main():
    genai.configure(api_key=GOOGLE_API_KEY)
    while True:
        query = recognize_speech().lower()
        instructions = "\nAnálise o texto caso faça sentido responder o que foi dito, reponda com uma frase curta de cumprimento que faça sentido com o que foi falado, pode usar o nome de wiki como seu, caso não responda com um none, seja educado. Exemplo caso seja chamado o nome Wiki, deve responder com olá meu nome é wiki como posso ajudar, ou com bom dia, boa noite, tudo bem, caso chamado o nome pedro deve ignorar. Texto a ser interpretado: "
        text = query + instructions
        response = model.generate_content(text)
        print(response.text)

        if response.text != None and "None" not in response.text and "none" not in response.text:
            speak(response.text)
            talk()
        # if "wiki" in query or "boa tarde wiki" in query or "bom dia wiki" in query or "boa noite wiki" in query or "Olá wiki" in query:
        #     if "boa tarde" in query:
        #         speak("boa tarde")
        #     if "boa noite" in query:
        #         speak("boa noite")
        #     if "bom dia" in query:
        #         speak("bom dia")
        #     talk()
main()
