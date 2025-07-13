import requests
import smtplib
from email.mime.text import MIMEText
import os

def get_cat_fact():
    try:
        response = requests.get("https://meowfacts.herokuapp.com/")
        response.raise_for_status()
        return response.json()["data"][0]
    except Exception as e:
        return f"Error fetching cat fact: {e}"

def send_email(fact):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    msg = MIMEText(fact)
    msg["Subject"] = "🐱 Daily Cat Fact Just for You!"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Email sent successfully!")

if __name__ == "__main__":
    fact = get_cat_fact()
    send_email(fact)
