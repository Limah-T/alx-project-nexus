from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import os

host_user = os.environ.get("EMAIL_HOST_USER")

@shared_task
def send_email(subject, txt_template, html_template, context, email):
    text_content = render_to_string(
        template_name=txt_template,
        context=context)

    html_content = render_to_string(
        template_name=html_template,
        context=context)
    
    msg = EmailMultiAlternatives(
            subject=subject, body=text_content, 
            from_email=host_user, to=[email])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception as e:
        pass
