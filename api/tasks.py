from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import smtplib, os

# host = os.environ.get("EMAIL_HOST")
# port = int(os.environ.get("EMAIL_PORT"))
host_user = os.environ.get("EMAIL_HOST_USER")
# host_password = os.environ.get("EMAIL_HOST_PASSWORD")

def send_email(subject, txt_template, html_template, context, user):
    text_content = render_to_string(
        template_name=txt_template,
        context=context)

    html_content = render_to_string(
        template_name=html_template,
        context=context)
    
    msg = EmailMultiAlternatives(
            subject=subject, body=text_content, 
            from_email=host_user, to=[user.email])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception as e:
        print(str(e))