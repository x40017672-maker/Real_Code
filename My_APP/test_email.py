from dotenv import load_dotenv
import smtplib 
import os

load_dotenv()

email = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")

print("Email loaded:", bool(email))
print("Password loaded:", bool(password))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email, password)
        print("Gmail authentication successful!")

except Exception as error:
    print(type(error).__name__, ":", error)