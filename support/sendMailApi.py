from django.template.loader import get_template
from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from email.MIMEImage import MIMEImage
import os
from django.conf import settings
from xhtml2pdf import pisa
from booking.models import booking
from .models import UserQuery
from emailahoy import VerifyEmail

def generic_mail(emailId, email_templates, email_contents, subject, images_list):
    template = get_template(email_templates)
    html_body = template.render(email_contents)
    msg = EmailMultiAlternatives(subject, html_body, settings.EMAIL_HOST_USER, [emailId])
    msg.attach_alternative(html_body, "text/html")

    msg.mixed_subtype = 'related'
    for f in images_list:
        fp = open(os.path.join(settings.BASE_DIR, 'templates', 'mail', 'images', f), 'rb') #images path
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header('Content-ID', '<{}>'.format(f))
        msg.attach(msg_img)

    msg.send()

def sendWelcomeMail(name, email):
    generic_mail(emailId=email, email_templates='welcome.html', email_contents={"name": name.title()}, subject='Welcome to goryd', images_list=['logo.png', 'why-us.jpg', 'sharing-bg.jpg'])

def send_on_confirmed_booking(email, content, email_templates="welcome.html"):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Confirmed For "+content['carMakeModel']
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

def send_on_new_booking(email, content, email_templates='welcome.html'):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Request For "+content['carMakeModel']
    try:
        generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])
    except:
        #mail cannot be sent
        b = booking.objects.filter(bookingId=content['bookingID'], error=None).first()
        if b:
            b.error = "Mail cannot be sent"
            b.save()

def send_on_cancel_booking(email, content, email_templates="welcome.html"):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Cancelled For "+content['carMakeModel']
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

def send_on_no_answer(email, content, email_templates="welcome.html"):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Cancelled For "+content['carMakeModel']
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

def send_on_reject_booking(email, content, email_templates='welcome.html'):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Rejected For "+content['carMakeModel']
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

def send_on_registration(email, content, email_templates='registration.html'):
    subject = "Goryd - New User Registration"
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=['logo.png'])

def send_on_new_ticket(email, content, email_templates='welcome.html'):
    subject = "[Ticket ID-"+content['ticket']+"] Goryd-New Ticket Submission"
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=['logo.png', 'why-us.jpg', 'sharing-bg.jpg'])

def send_reminder(email, content, email_templates='welcome.html'):
    subject = "[Booking ID-"+content['bookingID']+"] Goryd-Booking Location Of "+content['carMakeModel']
    generic_mail(emailId=email, email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

def send_on_new_query(email, content, email_templates='welcome.html'):
    #content -> issueId, query, subject, email and fullname of user

    e = VerifyEmail()
    status = e.verify_email_smtp(email=email)

    if e.was_found(status):
        #send thankyou mail to user
        subject = "Goryd - Our team will get in touch with you soon."
        generic_mail(emailId=email, email_templates='thanks.html', email_contents='', subject=subject, images_list=[])
        q = UserQuery.objects.get(pk=content['IssueId'])
        q.verified = True
        q.save()
        subject = "[Verified][Issue ID-"+str(content['IssueId'])+"] New Issue-"+content['subject']
    else:
        subject = "[NotVerified][Issue ID-"+str(content['IssueId'])+"] New Issue-"+content['subject']

    #send mail to support@goryd.in
    content['email'] = email
    generic_mail(emailId='support@goryd.in', email_templates=email_templates, email_contents=content, subject=subject, images_list=[])

# similarly you can create more helper mails

def generatePDF(template):
    sourcecHTML = get_template(template)
    outputFile = "test.pdf"
    resultFile = open(outputFile, "w+b")
    pdf = pisa.CreatePDF(sourcecHTML.render({}), dest=resultFile, link_callback=link_callback)
    resultFile.close()
    return pdf.err

def link_callback(uri, rel):
    if uri == "cid:logo.png":
        path = os.path.join(settings.BASE_DIR, 'templates', 'welcome', 'images', 'logo.png')
    if uri == "cid:sharing-bg.jpg":
        path = os.path.join(settings.BASE_DIR, 'templates', 'welcome', 'images', 'sharing-bg.jpg')
    if uri == "cid:why-us.jpg":
        path = os.path.join(settings.BASE_DIR, 'templates', 'welcome', 'images', 'why-us.jpg')
    return path
