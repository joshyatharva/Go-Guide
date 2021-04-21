import smtplib

list = [ ]
receiver = 'tembhurnerunal@gmail.com'

sender = 'goguide.seproject@gmail.com'
password = 'goguide@coep'

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    smtp.login(sender, password)

    subject = 'Registration'
    body = 'Booking successful \n - Go Guide'

    msg = f'Subject: {subject}\n\n{body}'

    smtp.sendmail(sender, receiver, msg)

#    for a in list:
#        smtp.sendmail('sherlockitis221b@gmail.com', a, msg)
