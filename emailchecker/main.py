import os
import time
import email
import imaplib
import argparse

from email.header import decode_header
from pathlib import Path


class EmailResponseSender:
    def execute(self, message, sender, sender_password, receiver, smpt_server):
        print(f'Sending response message "{message}" to {receiver}...')


class EmailChecker:
    def execute(self, sender, sender_password, imap_server):
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(sender, sender_password)
        mail.select('inbox')
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            return
        response_message = None
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
            x = msg.get('From')
            if subject.lower().startswith('emailchecker'):
                response_message = f'Found command {subject} from {x}!'
        mail.close()
        mail.logout()
        return response_message


def main():
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('computer_name', help='Computer name')
    parser.add_argument('--sender', help='Username of email account to use for checking emails (default: ralph.brecheisen@gmail.com)', default='ralph.brecheisen@gmail.com')
    parser.add_argument('--sender_password', help='Password of email account to use for checking email (if not provided will be loaded from file $HOME/emailchecker-password.txt)')
    parser.add_argument('--receiver', help='Email address to use to send responses (default: r.brecheisen@maastrichtuniversity.nl)', default='r.brecheisen@maastrichtuniversity.nl')
    parser.add_argument('--imap_server', help='IMAP server to use for checking emails (default: imap.gmail.com)', default='imap.gmail.com')
    parser.add_argument('--smtp_server', help='SMTP server to use for sending responses (default: smtp.gmail.com)', default='smtp.gmail.com')
    parser.add_argument('--interval', help='Interval in seconds to check for email (default: 5)', default=5)
    parser.add_argument('--print_args', help='Prints argument values before running email checker (default: "false"). To enable, set to "true" or "yes"', default='false')
    args = parser.parse_args()
    # Check arguments and load password if not provided
    if not args.sender_password:
        with open(os.path.join(Path.home(), 'emailchecker-password.txt'), 'r') as f:
            args.sender_password = f.readline().strip()
    if isinstance(args.interval, str):
        try:
            args.interval = int(args.interval)
        except ValueError:
            print(f'ERROR: --interval must be an integer value')
            return
    args.print_args = True if args.print_args == 'true' or args.print_args == 'yes' else False
    if args.print_args:
        print(args)
    # Start checking emails every 'interval'
    print(f'Starting email checker every {args.interval} seconds (stop using Ctrl+C)...')
    while True:
        checker = EmailChecker()
        reponse_message = checker.execute(args.sender, args.sender_password, args.imap_server)
        if reponse_message:
            sender = EmailResponseSender()
            sender.execute(reponse_message, args.sender, args. sender_password, args.receiver, args.smtp_server)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()