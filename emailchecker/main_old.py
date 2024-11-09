import os
import time
import email
import imaplib

from email.header import decode_header


def send_response(message, sender, receiver, password):
    import smtplib
    from email.mime.text import MIMEText
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = sender
    receiver_email = receiver
    password = password
    msg = MIMEText(message)
    msg["Subject"] = "EmailChecker response"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def check_email(sender, receiver, password, imap_server):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(sender, password)
    mail.select("inbox")
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        return
    for num in messages[0].split():
        status, msg_data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        from_ = msg.get("From")
        print(f"Processing email from {from_} with subject: {subject}")
        if subject.startswith('EmailChecker'):
            items = [x.trim() for x in subject.split(' ')]
            application, nr_lines, log_mode = items[1], items[2], 'error'
            if len(items) == 4:
                log_mode = items[3]
            print(f'Found following command: "EmailChecker {application} {nr_lines}, {log_mode}')
            send_response('This is my response!', sender, receiver, password)
    mail.close()
    mail.logout()



def main():
    print(f'Running EmailChecker...')
    print('Getting email credentials for Gmail IMAP server...')
    sender = os.getenv('EMAILCHECKER_SENDER', None)
    password = os.getenv('EMAILCHECKER_PASSWORD', None)
    receiver = os.getenv('EMAILCHECKER_RECEIVER', None)
    imap_server = 'imap.gmail.com'
    print(f'Found following credentials:')
    print(f'Sender: {sender}, receiver: {receiver}, password: {password}, IMAP server: {imap_server}')
    if not sender or not password:
        raise RuntimeError('Could not load sender, receiver or password from environment')
    time_to_wait = int(os.getenv('EMAILCHECKER_TIME_TO_WAIT', 60))
    while True:
        print('Checking email...')
        check_email(sender, receiver, password, imap_server)
        time.sleep(time_to_wait)


if __name__ == '__main__':
    main()