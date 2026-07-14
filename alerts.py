from database.mongodb import users_collection, alerts_collection
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from geolocation import get_location


EMAIL = "muthupandi.m1545@gmail.com"
PASSWORD = "dvszcopzllqpwesj"

print(get_location("8.8.8.8"))
def get_user_details(username):

    user = users_collection.find_one({"username": username})

    if user:
        email = user.get("email")
        phone = user.get("phone")

        return email, phone

    return None, None



def send_email_alert(user_email, message):

    msg = MIMEText(message)

    msg['Subject'] = "🚨 Security Alert"
    msg['From'] = EMAIL
    msg['To'] = user_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)

    if user_email:
        server.sendmail(EMAIL, user_email, msg.as_string())
    else:
        print("⚠ No email found for user")


    server.quit()


def security_alert(user, ip, file, risk):
    location = get_location(ip)
    email, phone = get_user_details(user)

    message = f"""
🚨 BLOCKCHAIN SECURITY ALERT

User : {user}
IP : {ip}
File : {file}
Risk Score : {risk}

Suspicious activity detected.
"""

    if email:
        send_email_alert(email, message)
    else:
        print("User email not found, skipping email alert")


    alerts_collection.insert_one({
        "user": user,
        "ip": ip,
        "file": file,
        "risk": risk,
        "time": str(datetime.now())
    })





