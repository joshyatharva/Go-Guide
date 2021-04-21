import smtplib

sender = 'goguide.seproject@gmail.com'
password = 'goguide@coep'

def mail(receiver, subject, body):
	try :
		with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
		    smtp.ehlo()
		    smtp.starttls()
		    smtp.ehlo()
		    smtp.login(sender, password)
		    msg = f'Subject: {subject}\n\n{body}'
		    smtp.sendmail(sender, receiver, msg)
		return True
	except Exception as e:
		print(f"Error While Sending Mail :: {e}")
		return False
