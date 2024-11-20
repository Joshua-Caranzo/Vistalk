
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import request, jsonify
import random
import string
from datetime import datetime, timedelta
from db import get_db_connection
import re


def generate_confirmation_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(recipient_email, subject, message):
    if not recipient_email:
        return "No email provided", 400
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "vistalk101@gmail.com"
    app_password = "cevb navk gira eqzu"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    body = message
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({
            'isSuccess': True,
            'message': 'Email successfuly sent',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    
    except Exception as e:
        return f"Failed to send email: {str(e)}", 500
    
def store_verification_code(email):
    confirmation_code = generate_confirmation_code()
    expiration_time = datetime.now() + timedelta(minutes=10)  
    conn = get_db_connection()

    cursor = conn.cursor()

    
    cursor.execute("""
        INSERT INTO email_verifications (email, confirmation_code, expiration_time)
        VALUES (%s, %s, %s)
    """, (email, confirmation_code, expiration_time))

    conn.commit()
    cursor.close()
    conn.close()

    return confirmation_code

def send_code_to_email():
    email = request.args.get('email')
    confirmation_code = store_verification_code(email)
    subject = "Your Verification Code"
    message = f"Your verification code is: {confirmation_code}"
    
    send_email(email, subject, message)
    return jsonify({
                'isSuccess': True,
                'message': 'Code sent successfully, please check your email.',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200 

def verify_code():
    email = request.args.get('email')
    code = request.args.get('code')
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT confirmation_code, expiration_time, is_verified
        FROM email_verifications
        WHERE email = %s AND confirmation_code = %s
    """, (email, code))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        confirmation_code, expiration_time, is_verified = result
        if datetime.now() > expiration_time:
            return jsonify({
                'isSuccess': False,
                'message': 'Code is already expired, try resending code',
                'data': None,
                'data2': None,
                'totalCount': None
            }), 200
        elif is_verified:
            return jsonify({
            'isSuccess': False,
            'message': 'Code is already expired, try resending code',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
        elif confirmation_code == code:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_verifications
                SET is_verified = TRUE
                WHERE email = %s
            """, (email,))
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
            'isSuccess': True,
            'message': 'Email verified',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    else:
        return jsonify({
            'isSuccess': False,
            'message': 'Invalid Code',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    

def is_email_used():
    email_to_check = request.args.get('email')

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email_to_check):
        return jsonify({
            'isSuccess': False,
            'message': 'Invalid email format. Please enter a valid email address.',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM user WHERE email = %s"
    cursor.execute(query, (email_to_check,))
    (count,) = cursor.fetchone()

    if count > 0:
        return jsonify({
            'isSuccess': False,
            'message': 'Email is already used. Please use another email.',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    else:
        return jsonify({
            'isSuccess': True,
            'message': 'Email is available to be used.',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200
    
def sendEmailToUs():
    sender = request.args.get('email')
    message = request.args.get('message')
    if not sender or not message:
        return jsonify({
            'isSuccess': False,
            'message': 'Email and message are required.',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 400
    
    subject = "New Message from Contact Us" 
    email_message = f"Message from: {sender}\n\n{message}"  

    send_email("vistalk101@gmail.com", subject, email_message)

    return jsonify({
            'isSuccess': True,
            'message': 'Successfully sent the message.',
            'data': None,
            'data2': None,
            'totalCount': None
        }), 200