import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
# Assuming database connection exists

# Email Configuration (Set up an App Password for Gmail)
EMAIL_SENDER = "sritanmai29@gmail.com"
EMAIL_PASSWORD = "arzj wnoa bojy uvno"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Telegram Configuration (Create a bot via @BotFather and get the bot token & chat ID)
TELEGRAM_BOT_TOKEN = "7506927710:AAHLMtDFtSLeuuzGLEAKRua34FGjMrFSI4A"
TELEGRAM_CHAT_ID = "2133296929"

def send_email(recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipient, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=data)
        print("Telegram message sent!", response.json())
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def check_expiring_products():
    from app import get_db_connection
    db = get_db_connection()
    cursor = db.cursor()
    
    one_week_later = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT product_id, name, expiry_date, user_id FROM products WHERE expiry_date = %s AND notified=0", (one_week_later,))
    products = cursor.fetchall()
    
    for product in products:
        product_id, name, expiry, producer_id = product
        
        # Get producer details
        cursor.execute("SELECT email, phone FROM users WHERE id = %s", (producer_id,))
        producer = cursor.fetchone()
        producer_email, producer_phone = producer if producer else (None, None)
        
        # Get warehouse manager and shopkeeper details from users table
        cursor.execute("SELECT email FROM users WHERE role = 'Warehouse Manager'")
        warehouse_manager = cursor.fetchone()
        warehouse_email = warehouse_manager[0] if warehouse_manager else None
        
        cursor.execute("SELECT email FROM users WHERE role = 'Shopkeeper'")
        shopkeeper = cursor.fetchone()
        shopkeeper_email = shopkeeper[0] if shopkeeper else None
        
        subject = f"Expiry Alert: {name} Expires Soon"
        body = f"Reminder: The product '{name}' is expiring on {expiry}. Please take necessary action."
        
        # Send notifications
        if producer_email:
            send_email(producer_email, subject, body)
        if warehouse_email:
            send_email(warehouse_email, subject, body)
        if shopkeeper_email:
            send_email(shopkeeper_email, subject, body)
        
        send_telegram_message(f"[Expiry Alert] {name} is expiring on {expiry}!")
        #cursor.fetchall()
        # Mark as notified
        cursor.execute("UPDATE products SET notified = 1 WHERE product_id = %s", (product_id,))
        db.commit()
    
    db.close()


# Schedule this function to run daily using a cron job or a task scheduler
