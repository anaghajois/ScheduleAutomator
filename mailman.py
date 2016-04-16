import mechanizer
import mailer

slots = mechanizer.startMechanizing()
print slots
mailer.sendAvailabilityUpdate(slots, "Availability Update")