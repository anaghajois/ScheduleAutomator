import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import dbhandler
import util
import os

def sendEmailUpdates(body, subject):
    print "Sending emails"
    # me == my email address
    # you == recipient's email address
    me = os.environ['UPDATE_SENDER_EMAIL']
    you = os.environ['UPDATE_RECEIVER_EMAIL']

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you



    mailPart = MIMEText(body, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(mailPart)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(os.environ['UPDATE_SENDER_EMAIL'], os.environ['UPDATE_SENDER_PASSWORD'])
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


def getAvailableSlotsMsg(timestamps):
    websiteUrl = os.environ['WEBSITE_URL']
    slotMessage = ''
    welcomeMessage = "Hello Dan! <br> "
    # Create the body of the message (a plain-text and an HTML version).
    if len(timestamps) == 0:
        welcomeMessage += "<h3>There are no empty slots in the next 36 hours</h3>"
    else:
        dbh = dbhandler.dbhandler()
        #delete all timestamps more than 2 days old
        dbh.deleteOldTimestamps(timestamps[0] + (2 * 24 * 60 * 60))

        welcomeMessage += "<h3>The following slots are available within 36 hours:</h3><br>"
        for timestamp in timestamps:
            exists = dbh.exists(timestamp)
            if not exists:
                dbh.addToDb(timestamp)

            slot = util.getDateTime(timestamp)
            curMessage = "<p>"
            curMessage += "EXISTING" if exists else "NEW"
            curMessage += " SLOT: "
            curMessage += slot.strftime("%a %I:%M %p, %b %d") + " - "
            reservationLink = "<a href=" + websiteUrl + "/reserve?timestamp=" + str(timestamp) + ">"
            reservationLink += "Click here to reserve" + "</a>"

            slotMessage += curMessage + reservationLink + "</p>"
        print slotMessage
    html = welcomeMessage + slotMessage
    return html

def getMyReservedSlotsMsg(timestamps):
    welcomeMessage = "<br>"
    slotMessage = ""
    if len(timestamps) == 0:
        welcomeMessage += "<h3>You don't have any reserved slots in the next 36 hours</h3>"
    else:
        dbh = dbhandler.dbhandler()
        welcomeMessage += "<h3>The following slots in the next 36 hours have been reserved by you:</h3><br>"
        for timestamp in timestamps:
            slot = util.getDateTime(timestamp)
            curMessage = "<p>"
            curMessage += " SLOT: "
            curMessage += slot.strftime("%a %I:%M %p, %b %d")

            slotMessage += curMessage + "</p>"
        print slotMessage
    html = welcomeMessage + slotMessage
    return html


def sendAvailabilityUpdate(timestamps, subject):
    body = getAvailableSlotsMsg(timestamps[0])
    body += getMyReservedSlotsMsg(timestamps[1])
    sendEmailUpdates(body, subject)

def sendReservationStatus(body):
    sendEmailUpdates(body, "Reservation Status")
