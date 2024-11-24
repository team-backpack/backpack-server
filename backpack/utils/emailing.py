import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_PASSWORD
from flask import render_template

port = 465
smtp_server = "smtp.gmail.com"
from_email = "social.backpack.bp@gmail.com"
password = EMAIL_PASSWORD

def send(to_email: str, subject: str, body: str):

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message.as_string())