import requests
from datetime import datetime, timedelta, timezone
import telebot
import time
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot multilingua è vivo"

def run_web_server():
    port = int(os.environ.get("PORT", 10000)) 
    print(f"Avvio Web Server sulla porta {port}...")
    app.run(host='0.0.0.0', port=port)

TOKEN_TELEGRAM = "8910104115:AAEtEZtzhkcj0jXkZt5PPpRONzWVfCUdxdw"
API_KEY_NEWS = "7d607a1e6a6946ceb49412b3c191f24b"
CHAT_ID = -1003900755137

bot = telebot.TeleBot(TOKEN_TELEGRAM)

def ottieni_notizie_ai():
    """Scarica le notizie in Italiano, Inglese e Ucraino usando le virgolette di sicurezza"""
    url = "https://newsapi.org/v2/everything"
    lingue = ["it", "en", "uk"]
    tutte_le_notizie = []

    print("🔄 Avvio download notizie multilingua...")

    for lingua in lingue:
        
        if lingua == "it":
            query = '"Intelligenza Artificiale"'
        elif lingua == "uk":
            query = '"Штучний Інтелект"'
        else:
            query = '"Artificial Intelligence"'

        parametri = {
            "q": query,
            "language": lingua,
            "sortBy": "publishedAt",
            "apiKey": API_KEY_NEWS
        }
        try:
            risposta = requests.get(url, params=parametri)
            dati = risposta.json()
            
            # SEZIONE DI CONTROLLO: Vediamo se l'API ci restituisce un errore nascosto
            if dati.get("status") == "error":
                print(f"❌ Errore API [{lingua.upper()}]: {dati.get('message')}")
                continue

            articoli = dati.get("articles", [])
            print(f"   - Scaricate {len(articoli)} notizie in [{lingua.upper()}]")
            tutte_le_notizie.extend(articoli)
        except Exception as e:
            print(f"Errore nel download delle notizie per la lingua {lingua}: {e}")

    # Ordiniamo per data (dalla più recente)
    tutte_le_notizie.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    
    print(f"📊 Totale notizie combinate e ordinate: {len(tutte_le_notizie)}")
    return tutte_le_notizie

def invia_post_telegram(articolo):
    """Prende un singolo articolo e lo trasforma in un post Telegram"""
    titolo = articolo.get("title", "Nessun Titolo")
    link = articolo.get("url", "")
    foto = articolo.get("urlToImage") 
    descrizione = articolo.get("description", "Clicca il link per leggere i dettagli.")

    if not descrizione:
        descrizione = "Clicca il link per leggere i dettagli."

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
        print(f"✅ Post inviato correttamente alle ore {datetime.now().hour}")
    except Exception as e:
        print(f"❌ Errore nell'invio a Telegram: {e}")


def ciclo_bot():
    """Ciclo di automazione: analizza la lista globale multilingua con controlli rigidi"""
    print("Il Bot è attivo e sta monitorando l'orario...")
    notizie = ottieni_notizie_ai()
    indice_notizia = 0

    while True:
        ora_attuale_dt = datetime.now(timezone.utc)
        ora_attuale = ora_attuale_dt.hour

        # Controlla la fascia oraria dalle 8 alle 23
        if 8 <= ora_attuale <= 23:
            if indice_notizia < len(notizie):
                notizia_da_inviare = notizie[indice_notizia]
                
               
                titolo_lower = notizia_da_inviare.get("title", "").lower()
                parole_chiave = ["intelligenza", "artificial", "ai", "штучний", "інтелект"]

                if not any(parola in titolo_lower for parola in parole_chiave):
                    print(f"⏩ Articolo scartato (Non parla di IA nel titolo): {notizia_da_inviare.get('title')[:40]}...")
                    indice_notizia += 1
                    continue 
                
              
                data_pubblicazione_str = notizia_da_inviare.get("publishedAt")
                
                if data_pubblicazione_str:
                    try:
                        data_pubblicazione = datetime.fromisoformat(data_pubblicazione_str.replace('Z', '+00:00'))
                        limite_temporale = ora_attuale_dt - timedelta(hours=48)
                        
                        if data_pubblicazione < limite_temporale:
                            print(f"⏩ Trovate solo notizie vecchie di oltre 48 ore nella lista globale. Mi metto in attesa...")
                            indice_notizia = len(notizie) 
                            time.sleep(3600) 
                            continue 
                            
                    except Exception as e:
                        print(f"Errore nel parsing della data: {e}")

                # Se supera entrambi i filtri, la invia
                invia_post_telegram(notizia_da_inviare)
                indice_notizia += 1
                time.sleep(3600) # Aspetta un'ora tra un invio valido e l'altro
            else:
                print("Nessuna nuova notizia fresca nelle 3 lingue. Aspetto 1 ora prima di riscaricare...")
                time.sleep(3600) 
                notizie = ottieni_notizie_ai() 
                indice_notizia = 0
        else:
            print("Fascia notturna: il bot riposa...")
            time.sleep(600)


if __name__ == "__main__":  
    t = Thread(target=ciclo_bot)
    t.daemon = True
    t.start()
    
    run_web_server()    