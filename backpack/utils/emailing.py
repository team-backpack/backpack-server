import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_PASSWORD

port = 465
smtp_server = "smtp.gmail.com"
from_email = "social.backpack.bp@gmail.com"
password = EMAIL_PASSWORD

def send(to: str = "", subject: str = "", body: str = ""):

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to, message.as_string())


def send_token(email: str, token: str = ""):
    with open("backpack/templates/token.html", mode="r", encoding="UTF-8") as file:
        body = file.read()
        body = body.format(token)

        send(to=email, subject="Seja bem-vindo ao Backpack, aventureiro!", body=body)
