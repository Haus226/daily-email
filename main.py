import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime
import random

OPENROUTER_API = os.getenv("OPENROUTER_API")

start_date = datetime(2021, 11, 2)
anniversary = datetime(datetime.now().year, 11, 2)

def fetch_cat_fact():
    try:
        fact_resp = requests.get("https://meowfacts.herokuapp.com/", timeout=5)
        fact = fact_resp.json()['data'][0]

        image_resp = requests.get("https://api.thecatapi.com/v1/images/search", timeout=5)
        image_url = image_resp.json()[0]['url']

        return f"""
        <div class="section-card cat-section">
            <h2 class="section-title">🐱 Cat Fact of the Day</h2>
            <div class="content-wrapper">
                <p class="fact-text">{fact}</p>
                <div class="image-container">
                    <img src="{image_url}" alt="Adorable Cat" class="cat-image"/>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""<div class="section-card error-section">
            <h2 class="section-title">🐱 Cat Fact</h2>
            <p class="error-text">Failed to fetch cat fact or image: {e}</p>
        </div>"""

def fetch_quote():
    try:
        with open('quotes.txt', 'r', encoding='utf-8') as file:
            quotes = file.readlines()
        if not quotes:
            return """<div class="section-card quote-section">
                <h2 class="section-title">💬 Quote</h2>
                <p class="quote-text">No more quotes left in quotes.txt.</p>
            </div>"""
        # Save back without the first line
        with open("quotes.txt", "w", encoding='utf-8') as file:
            file.writelines(quotes[1:])
        return f"""
        <div class="section-card quote-section">
            <h2 class="section-title">💬 Quote of the Day</h2>
            <div class="quote-container">
                <p class="quote-text">"{quotes[0].strip()}"</p>
                <div class="quote-decoration">✧･ﾟ: *✧･ﾟ:*</div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""<div class="section-card error-section">
            <h2 class="section-title">💬 Quote</h2>
            <p class="error-text">Failed to fetch quote: {e}</p>
        </div>"""

def fetch_affirmation():
    try:
        r = requests.get("https://www.affirmations.dev/", timeout=5)
        return r.json().get("affirmation", "You are amazing and capable!")
    except Exception:
        return "You are amazing and capable!"

def fetch_fun_fact():
    try:
        r = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en", timeout=5)
        return f"""
        <div class="section-card fun-fact-section">
            <h2 class="section-title">🧠 Fun Fact</h2>
            <div class="fact-container">
                <p class="fun-fact-text">{r.json()['text']}</p>
                <div class="fact-icon">🤓</div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""<div class="section-card error-section">
            <h2 class="section-title">🧠 Fun Fact</h2>
            <p class="error-text">😿 Failed to fetch a fun fact. Error: {e}</p>
        </div>"""

def fetch_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        joke = r.json()
        setup = joke['setup']
        punchline = joke['punchline']
        full_joke = f"{setup} {punchline}"

        prompt = f"""
            You are a witty assistant who explains jokes clearly and briefly.
            Explain the humor in this joke in 1-2 short sentences:

            "{full_joke}"

            Avoid being too dry or too literal.
        """

        res = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "mistralai/mistral-nemo:free",
                "messages": [{"role": "user", "content": prompt}]
            }),
            timeout=10
        )
        explanation = res.json().get("choices", [{}])[0].get("message", {}).get("content", "No explanation available.").strip()

        return f"""
        <div class="section-card joke-section">
            <h2 class="section-title">🃏 Joke of the Day</h2>
            <div class="joke-container">
                <p class="joke-setup">{setup}</p>
                <p class="joke-punchline">{punchline}</p>
                <div class="joke-explanation">
                    <div class="explanation-header">🤖 Why it's funny:</div>
                    <p class="explanation-text">{explanation}</p>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""<div class="section-card error-section">
            <h2 class="section-title">🃏 Joke of the Day</h2>
            <p class="error-text">Failed to load joke or explanation. Error: {e}</p>
        </div>"""

def fetch_tarot_card():
    try:
        random.seed(datetime.now().strftime("%Y%m%d"))
        cards = json.loads(open("tarot_cards/tarot.json", "r", encoding="utf-8").read())
        card = cards["cards"][random.randint(0, len(cards["cards"]) - 1)]
        name = card["name"]
        meaning = card["meaning_up"]
        desc = card.get("desc", "")
        image_url = card.get("image", "")
        
        prompt = f"""
        You are a warm and uplifting tarot advisor. The user has drawn the "{name}" tarot card.

        Card Meaning: "{meaning}"

        Card Description: "{desc}"

        Write a short, kind, and encouraging 2-3 sentence daily guidance inspired by this card. Make it feel supportive, reassuring, and hopeful, never negative or ominous.

        Avoid repeating the card name. Speak as if gently guiding a friend to have a beautiful day.
        """

        res = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "mistralai/mistral-nemo:free",
                "messages": [{"role": "user", "content": prompt}]
            }),
            timeout=10
        )
        guidance = res.json().get("choices", [{}])[0].get("message", {}).get("content", "No explanation available.").strip()

        return f"""
        <div class="section-card tarot-section">
            <h2 class="section-title">🔮 Tarot Card of the Day</h2>
            <div class="tarot-container">
                <h3 class="card-name">{name}</h3>
                
                <div class="card-image-wrapper">
                    <img src='{image_url}' alt='{name}' class="tarot-image" />
                </div>
                
                <div class="meaning-section">
                    <div class="meaning-title">✨ Core Meaning</div>
                    <p class="meaning-text">{meaning}</p>
                </div>
                
                <div class="description-section">
                    <div class="description-title">📜 Description</div>
                    <p class="description-text">{desc}</p>
                </div>
                
                <div class="explanation-section">
                    <div class="explanation-title">🔍 Daily Guidance</div>
                    <p class="guidance-text">{guidance}</p>
                </div>
                
                <div class="mystical-elements">
                    ✧･ﾟ: *✧･ﾟ:* ⭐ *:･ﾟ✧*:･ﾟ✧
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""<div class="section-card error-section">
            <h2 class="section-title">🔮 Tarot</h2>
            <p class="error-text">Failed to fetch tarot card: {e}</p>
        </div>"""

def get_styles():
    return """
    <style>
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            color: #333;
        }
        
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            padding: 40px;
            backdrop-filter: blur(10px);
        }
        
        .main-title {
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .affirmation-section {
            text-align: center;
            background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
            border-left: 5px solid #e17055;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .affirmation-text {
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3436;
            margin: 0;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }
        
        .love-journey {
            text-align: center;
            background: linear-gradient(135deg, #fd79a8, #e84393);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .love-journey h2 {
            margin-top: 0;
            font-size: 1.8em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .love-stats {
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .section-card {
            background: white;
            margin: 30px 0;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            overflow: hidden;
            border: 1px solid #e9ecef;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .section-title {
            background: linear-gradient(135deg, #2c1810, #4a2c2a);
            color: #d4af37;
            padding: 20px;
            margin: 0;
            font-size: 1.5em;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .content-wrapper, .joke-container, .fact-container, .quote-container, .tarot-container {
            padding: 25px;
        }
        
        /* Cat Section */
        .cat-section .section-title {
            background: linear-gradient(135deg, #ff7675, #fd79a8);
        }
        
        .fact-text {
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 20px;
            color: #2d3436;
        }
        
        .image-container {
            text-align: center;
        }
        
        .cat-image {
            max-width: 100%;
            max-height: 400px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border: 3px solid #fd79a8;
        }
        
        /* Joke Section */
        .joke-section .section-title {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
        }
        
        .joke-setup {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #2d3436;
            line-height: 1.5;
        }
        
        .joke-punchline {
            font-size: 1.2em;
            font-weight: bold;
            color: #0984e3;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .joke-explanation {
            background: linear-gradient(135deg, #ddd6fe, #c4b5fd);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #8b5cf6;
        }
        
        .explanation-header {
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 8px;
        }
        
        .explanation-text {
            margin: 0;
            color: #2d3436;
            line-height: 1.5;
        }
        
        /* Fun Fact Section */
        .fun-fact-section .section-title {
            background: linear-gradient(135deg, #00b894, #00cec9);
        }
        
        .fact-container {
            position: relative;
        }
        
        .fun-fact-text {
            font-size: 1.1em;
            line-height: 1.6;
            color: #2d3436;
            margin: 0;
            padding-right: 60px;
        }
        
        .fact-icon {
            position: absolute;
            top: 0;
            right: 0;
            font-size: 2em;
            opacity: 0.7;
        }
        
        /* Quote Section */
        .quote-section .section-title {
            background: linear-gradient(135deg, #a29bfe, #6c5ce7);
        }
        
        .quote-text {
            font-size: 1.2em;
            font-style: italic;
            color: #2d3436;
            text-align: center;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .quote-decoration {
            text-align: center;
            opacity: 0.7;
            color: #6c5ce7;
        }
        
        /* Tarot Section */
        .tarot-section .section-title {
            background: linear-gradient(135deg, #2c1810, #4a2c2a);
        }
        
        .card-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c1810;
            text-align: center;
            margin: 0 0 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }
        
        .card-image-wrapper {
            text-align: center;
            margin: 20px 0;
        }
        
        .tarot-image {
            max-width: 250px;
            width: 100%;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border: 2px solid #d4af37;
        }
        
        .meaning-section {
            background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #e17055;
        }
        
        .description-section {
            background: linear-gradient(135deg, #a8e6cf, #88d8c0);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #00b894;
        }
        
        .explanation-section {
            background: linear-gradient(135deg, #ddd6fe, #c4b5fd);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #8b5cf6;
        }
        
        .meaning-title, .description-title, .explanation-title {
            font-size: 0.95em;
            font-weight: bold;
            color: #2d3436;
            margin: 0 0 8px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .meaning-text, .description-text, .guidance-text {
            margin: 0;
            color: #2d3436;
            line-height: 1.5;
        }
        
        .meaning-text {
            font-style: italic;
            font-size: 1.05em;
        }
        
        .mystical-elements {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            color: #d4af37;
        }
        
        /* Error Section */
        .error-section .section-title {
            background: linear-gradient(135deg, #e17055, #d63031);
        }
        
        .error-text {
            color: #d63031;
            font-style: italic;
            padding: 15px;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                margin: 10px;
                padding: 20px;
                border-radius: 15px;
            }
            
            .main-title {
                font-size: 2em;
            }
            
            .section-title {
                font-size: 1.3em;
                padding: 15px;
            }
            
            .content-wrapper, .joke-container, .fact-container, .quote-container, .tarot-container {
                padding: 20px;
            }
            
            .fun-fact-text {
                padding-right: 0;
            }
            
            .fact-icon {
                position: static;
                display: block;
                text-align: center;
                margin-top: 10px;
            }
        }
    </style>
    """

def run():
    today = datetime.now()
    days_together = (today - start_date).days
    days_until = max((anniversary - today).days, 0)

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Delight</title>
        {get_styles()}
    </head>
    <body>
        <div class="main-container">
            <h1 class="main-title">🌟 Daily Delight 🌟</h1>
            
            <div class="affirmation-section">
                <h2 class="affirmation-text">🌈 {fetch_affirmation()}</h2>
            </div>
            
            <div class="love-journey">
                <h2>💕 Our Love Journey</h2>
                <div class="love-stats">
                    <p>We've been together for <strong>{days_together} days</strong> ✨</p>
                    <p>{'Only ' + str(days_until) + ' days until our anniversary! 🎉' if days_until > 0 else "💖 Happy Anniversary! 🎊"}</p>
                </div>
            </div>
            
            {fetch_cat_fact()}
            {fetch_tarot_card()}
            {fetch_joke()}
            {fetch_fun_fact()}
            {fetch_quote()}
        </div>
    </body>
    </html>
    """

def send_email(content_html):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("DELIGHT_EMAIL")

    if not all([sender, password, recipient]):
        raise EnvironmentError("Missing SENDER_EMAIL, SENDER_PASSWORD, or DELIGHT_EMAIL in environment variables.")

    msg = MIMEMultipart("alternative")
    msg['Subject'] = "💌 Your Daily Dose of Delight"
    msg['From'] = sender
    msg['To'] = recipient

    msg.attach(MIMEText(content_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(sender, password)
        s.send_message(msg)

def demo():
    content = run()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    # content = run()
    # send_email(content)
    demo()
    # fetch_tarot_card()