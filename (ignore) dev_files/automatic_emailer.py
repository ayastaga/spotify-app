from email.message import EmailMessage
import ssl
import smtplib

email_sender = 34734278984932
email_password = 34734278984932
email_reciever = 34734278984932

subject = '[DELETE THIS] Thank you for signing up! [DELETE THIS]'
body = """
Once again, thank you for signing up! 

You can ignore this email as it is a test. Please delete it. 

"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_reciever
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_reciever, em.as_string())

