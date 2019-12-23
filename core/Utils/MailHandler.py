import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.Utils.Constants.PathsConstants import MAILS_TEMPLATES_DIR, TEMPLATE_MAIL_NAME

PORT = 587
SMTP_SERVER_ADDR = "smtp.gmail.com"
API_MAIL_ADDR = "autograde.dev@gmail.com"
PASSWORD_ADDR = "autograde-api"
class MailHandler():

    @staticmethod
    def sendPlainTextMail(destMail, subject, content):
        context = ssl.create_default_context()
        server = None

        try:
            msg = MIMEMultipart('alt')
            msg.add_header('Content-Type', 'text/html')
            msg["subject"] = subject
            p2 = MIMEText(MailHandler.getMailTemplateAsStr().format(content=content), 'html')
            msg.attach(p2)
            server = smtplib.SMTP(SMTP_SERVER_ADDR, PORT)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(API_MAIL_ADDR, PASSWORD_ADDR)
            server.sendmail(API_MAIL_ADDR, destMail, msg.as_string())

        except Exception as e:
            print("[MailHandler - sendPlainTextMail] ex : ", e)
        finally:
            server.quit()


    @staticmethod
    def getMailTemplateAsStr():
        with open(MAILS_TEMPLATES_DIR + TEMPLATE_MAIL_NAME, 'r') as f:
            return str(f.read())