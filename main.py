import requests
import smtplib
import random
from email.mime.text import MIMEText
import os
from datetime import datetime


def get_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        joke = r.json()
        return f"🃏 Joke of the Day:\n\n{joke['setup']}\n{joke['punchline']}"
    except Exception as e:
        return f"😿 Failed to fetch a joke. Error: {e}"


def get_cat_fact():
    try: 
        r = requests.get("https://meowfacts.herokuapp.com/", timeout=5)
        return f"🐱 Cat Fact of the Day:\n\n{r.json()['data'][0]}"
    except Exception as e:
        return f"😿 Failed to fetch a cat fact. Error: {e}"


def get_quote():
    with open('quotes.txt', 'r', encoding='utf-8') as file:
        quotes = file.readlines()
    with open("quotes.txt", "w", encoding='utf-8') as file:
        file.writelines(quotes[1:])
    return f"💬 Quote of the Day:\n\n{quotes[0]}"

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

def get_content_by_day():
    day = datetime.now().strftime("%A")

    if day == "Monday":
        return get_cat_fact()
    elif day == "Tuesday":
        return get_quote()
    elif day == "Wednesday":
        return get_joke()
    else:
        choice = random.choice([get_cat_fact, get_joke, get_quote])
        return choice()

if __name__ == "__main__":
    content = get_content_by_day()
    send_email(content)
