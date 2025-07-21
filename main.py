import requests
import smtplib
import random
from email.mime.text import MIMEText
import os


def get_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        joke = r.json()
        return f"🃏 Joke of the Day:\n\n{joke['setup']}\n{joke['punchline']}"
    except:
        return "😿 Failed to fetch a joke."


def get_cat_fact():
    try: 
        r = requests.get("https://api.tangdouz.com/lzs.php", timeout=5)
        return f"🐱 Cat Fact:\n\n{r.text.strip()}"
    except:
        return "😿 Failed to fetch a cat fact."


def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = r.json()[0]
        return f"💡 Quote of the Day:\n\n“{data['q']}”\n— {data['a']}"
    except:
        return "😿 Failed to fetch a quote."


def send_email(content):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")

    if not all([sender, password, recipient]):
        raise EnvironmentError("Missing SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL in environment variables.")

    msg = MIMEText(content)
    msg['Subject'] = "🌟 Your Daily Dose of Delight"
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(sender, password)
        s.send_message(msg)
    print("✅ Email sent successfully!")


if __name__ == "__main__":
    # Randomly select one type of message
    choices = [get_joke, get_cat_fact, get_quote]
    chosen = random.choice(choices)
    message = chosen()
    send_email(message)
