import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def get_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        joke = r.json()
        return f"<h2>🃏 Joke of the Day</h2><p>{joke['setup']}<br><b>{joke['punchline']}</b></p>"
    except Exception as e:
        return f"<h2>🃏 Joke of the Day</h2><p><i>Failed to fetch joke: {e}</i></p>"

def get_cat_fact():
    try:
        fact_resp = requests.get("https://meowfacts.herokuapp.com/", timeout=5)
        fact = fact_resp.json()['data'][0]

        image_resp = requests.get("https://api.thecatapi.com/v1/images/search", timeout=5)
        image_url = image_resp.json()[0]['url']

        return f"""
            <h2>🐱 Cat Fact</h2>
            <p>{fact}</p>
            <div style="text-align: center;">
                <img src="{image_url}" alt="Cat Image" width="400"/>
            </div>
        """
    except Exception as e:
        return f"<h2>🐱 Cat Fact</h2><p><i>Failed to fetch cat fact or image: {e}</i></p>"

def get_quote():
    try:
        with open('quotes.txt', 'r', encoding='utf-8') as file:
            quotes = file.readlines()
        if not quotes:
            return "<h2>💬 Quote</h2><p><i>No more quotes left in quotes.txt.</i></p>"
        # Save back without the first line
        with open("quotes.txt", "w", encoding='utf-8') as file:
            file.writelines(quotes[1:])
        return f"<h2>💬 Quote of the Day</h2><p>{quotes[0]}</p>"
    except Exception as e:
        return f"<h2>💬 Quote</h2><p><i>Failed to fetch quote: {e}</i></p>"

def send_email(content_html):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("DELIGHT_EMAIL")

    if not all([sender, password, recipient]):
        raise EnvironmentError("Missing SENDER_EMAIL, SENDER_PASSWORD, or DELIGHT_EMAIL in environment variables.")

    msg = MIMEMultipart("alternative")
    msg['Subject'] = "🌟 Your Daily Dose of Delight"
    msg['From'] = sender
    msg['To'] = recipient

    msg.attach(MIMEText(content_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(sender, password)
        s.send_message(msg)

def run():
    return "<html><body>" + get_cat_fact() + get_joke() + get_quote() + "</body></html>"

def demo():
    content = run()
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    content = run()
    # send_email(content)
    demo()