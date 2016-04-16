from flask import Flask
from flask import request
import os
import mechanizer
import mailer
import util

app = Flask(__name__)
    
@app.route("/")
def hello():
    welcomeMessage = "Welcome Dan! <br> The available slots in the next 36 hours are<br>"
    slots = mechanizer.startMechanizing()
    slotMessage = ''
    for slot in slots:
        curMessage = str(slot.month) + " " + str(slot.day) + " " + slot.time().isoformat() + "<br>"
        slotMessage += curMessage
    
    return welcomeMessage + slotMessage

@app.route("/email")
def email():
    slots = mechanizer.startMechanizing()
    mailer.sendEmailUpdates(slots)
    return "sent emails"

@app.route("/reserve")
def reserve():
    timestamp = request.args.get('timestamp', "None")
    try:
        success = mechanizer.reserveTheSlotAt(timestamp)
        slot = util.getDateTime(timestamp)
        dateStr = slot.strftime("%a %I:%M %p, %b %d")
        message = "Hello Dan! <br>RESERVATION {} FOR {}".format("MADE" if success else "FAILED", dateStr)

        mailer.sendReservationStatus(message)
    except Exception, e:
        print "Exception: " + str(e)
    return message


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
    

