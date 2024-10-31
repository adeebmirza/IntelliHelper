import smtplib
import os
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from dotenv import load_dotenv

load_dotenv()

def send_email(sender_email,receiver_email,subject,body,password): 
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(sender_email,password)
        text = message.as_string()
        server.sendmail(sender_email,receiver_email,text)
        server.quit()
        print(" ")
    except Exception as e:
        print(f"Failed to send the email. Error: {e}")



def send(receiver_email,otp):
    sender_email = os.getenv("SENDER_EMAIL")
    subject = 'This is generated by the IntelliHelper application'
    body = f"We have received the signup request. Your six digit OTP: {otp}" 
    receiver_email = receiver_email
    password = os.getenv("SENDER_PASSWORD")
    send_email(sender_email,receiver_email,subject,body,password)


def send_forget(receiver_email,token):
    sender_email = os.getenv("SENDER_EMAIL")
    subject = 'This is generated by the IntelliHelper application'
    body = f"Your reset password link : http://127.0.0.1:5000//reset_password//{token}" 
    receiver_email = receiver_email
    password = os.getenv("SENDER_PASSWORD")
    send_email(sender_email,receiver_email,subject,body,password)