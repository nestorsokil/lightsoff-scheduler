import logging
import base64
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileName, FileType, FileContent, Disposition

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")


def send_email_with_invite(ics, to_emails):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    encoded_file = base64.b64encode(ics.encode('utf-8')).decode('ascii')

    mail = Mail(
        from_email=Email(SENDGRID_FROM_EMAIL),
        to_emails=[To(email) for email in to_emails],
        subject="LOE Update",
        plain_text_content=Content("text/plain", "Power-off schedule has just updated! Please check your calendar."))
    mail.attachment = Attachment(
        FileContent(encoded_file),
        FileName("invite.ics"),
        FileType("text/calendar"),
        Disposition('attachment')
    )

    try:
        logging.info("Sending email...")
        response = sg.send(mail)
        logging.info(f"Email sent with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
