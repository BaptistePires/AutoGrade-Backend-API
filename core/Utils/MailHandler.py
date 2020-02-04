import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
from core.Utils.Constants.PathsFilesConstants import MAILS_TEMPLATES_DIR, TEMPLATE_MAIL_NAME

PORT = 587
SMTP_SERVER_ADDR = "eu-west-1.amazonses.com"
API_MAIL_ADDR = "autograde.dev@gmail.com"
PASSWORD_ADDR = "autograde-api"
USERNAME = "AKIAQTP7HKD2POQMNEON"
PASSWORD = "BCmlh5nhRcqjgYgS/mMlb9mEw3f4AdKCIhSo7W4DpJeq"
SENDER = 'autograde.dev@gmail.com'
SENDERNAME = 'AutoGrade'

class MailHandler():

    @staticmethod
    def sendPlainTextMail(destMail, subject, content):
        context = ssl.create_default_context()
        server = None

        try:
            msg = MIMEMultipart('alt')
            msg.add_header('Content-Type', 'text/html')
            msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
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