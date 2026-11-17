
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from jokeapi import Jokes
import asyncio

# Email configuration (use environment variables)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

print("EMAIL_ADDRESS:", repr(EMAIL_ADDRESS))
print("EMAIL_PASSWORD loaded:", repr(EMAIL_PASSWORD))
print("RECIPIENT_EMAIL:", repr(RECIPIENT_EMAIL))

async def send_daily_joke():
    j = await Jokes()
    joke = await j.get_joke()

    msg = EmailMessage()
    msg["Subject"] = "😂 Your Daily Dose of Humor!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL

    msg.set_content(f"""
Good morning!

Here's your joke for today:

{joke["joke"] if joke["type"] == "single" else joke["setup"] + "\n" + joke["delivery"]}

Have a great day!

Your Daily Joke Bot 🤖
""")

    try:
        print("Connecting to Gmail...")

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(1)

            print("Starting TLS...")
            server.ehlo()
            server.starttls()
            server.ehlo()

            print("Logging into Gmail...")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            print("Sending email...")
            server.send_message(msg)

        print("SUCCESS! Email sent!")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(send_daily_joke())

