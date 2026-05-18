
import requests
from datetime import datetime
import telebot
import time
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Il bot è vivo"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

TOKEN_TELEGRAM = "8910104115:AAEtEZtzhkcj0jXkZt5PPpRONzWVfCUdxdw"
API_KEY_NEWS = "7d607a1e6a6946ceb49412b3c191f24b"
CHAT_ID = -1003900755137

bot = telebot.TeleBot(TOKEN_TELEGRAM)


def ottieni_notizie_ai():
    """Funzione che scarica le notizie e restituisce una lista di articoli"""
    url = "https://newsapi.org/v2/everything"
    parametri = {
        "q": "Artificial Intelligence OR Intelligenza Artificiale",
        "language": "it",
        "sortBy": "publishedAt",
        "apiKey": API_KEY_NEWS
    }

    try:
        risposta = requests.get(url, params=parametri)

        dati = risposta.json()
        return dati.get("articles",[])
    except Exception as e:
        print(f"Errore nel download delle notizie: {e}")
        return []

def invia_post_telegram(articolo):
    """Prende un singolo articolo e lo trasforma in un post Telegram con foto"""
    titolo = articolo.get("title", "Nessuno Titolo")
    link = articolo.get("url", "")
    foto = articolo.get("urlImage")
    descrizione = articolo.get("description", "Clicca il link per leggere i dettagli.")

    messaggio = (
        f"🤖 *NEWS IA DEL MOMENTO*\n\n"
        f"🔥 *{titolo}*\n\n"
        f"📝 {descrizione[:200]}...\n\n"
        f"🔗 [Leggi l'articolo completo]({link})"
    )

    try:
        if foto:
            bot.send_photo(CHAT_ID, foto, caption=messaggio, parse_mode="Markdown")
        else:
            bot.send_message(CHAT_ID, messaggio, parse_mode="Markdown")
        print(f"Post inviato correttamente alle ore {datetime.now().hour}")
    
    except Exception as e:
        print(f"Errore nell'invio a Telegram: {e}")


        # --- LOGICA DI AUTOMAZIONE ---


print("Il Bot è attivo e sta monitorando l'orario...")

notizie = ottieni_notizie_ai()
indice_notizia = 0

while True:
    ora_attuale = datetime.now().hour

    if 8 <= ora_attuale <= 23:
        if indice_notizia < len(notizie):
            notizia_da_inviare = notizie[indice_notizia]
            invia_post_telegram(notizia_da_inviare)

            indice_notizia += 1

            time.sleep(3600)
        else:

            notizie = ottieni_notizie_ai
            indice_notizia = 0
    else:
        print("Fascia notturna: il bot riposa...")
        time.sleep(600)


if __nome__ =="__main__":
    t = Thread(target=run_web_server)
    t.start()
    invia_post_telegram()
