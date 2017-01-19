from django.conf import settings
import urllib
import ctypes

libc = ctypes.cdll.LoadLibrary('libc.so.6')
res_init = libc.__res_init

loginId = settings.SMS_LOGIN_USER
loginPassword = settings.SMS_LOGIN_PASSWORD

def send_sms(phoneNumber, msg):
    encodedMsg = urllib.quote(msg)
    smsApi ='http://enterprise.smsgupshup.com/GatewayAPI/rest?'+'method=sendMessage&send_to=%s&v=1.1&msg=%s&msg_type=text&userid=%s&password=%s' % (phoneNumber, encodedMsg, loginId, loginPassword)
    print smsApi
    while True:
        try:
            res_init()
            response = urllib.urlopen(smsApi)
            break
        except:
            continue
    return response

def send_otp(phoneNumber, otp):
    msg = "Your OTP is %s." % (otp)
    send_sms(phoneNumber, msg)

def send_sms_on_booking(phoneNumber, customerName, bookingId):
    msg = "Dear %s,\nThank you for booking with Goryd. Your booking id is %s stands requested. You will receive a confirmation once the owner approves your request.\nTo view/cancel your booking click: http://www.goryd.in. For help, please call us at +91-9930467093." % (customerName, bookingId)
    send_sms(phoneNumber, msg)

def  send_sms_to_owner_on_booking(phoneNumber, ownerName, customerName):
    msg = "Dear %s, %s has requested to book your car. Please confirm it within 30 mins. Failing to do so will reject the request automatically. Click http://www.goryd.in." % (ownerName, customerName)
    send_sms(phoneNumber, msg)

def send_contact_number_to_customer(phoneNumber, bookingId, ownerPhone):
    msg = "With reference to booking id %s, the contact number of owner is %s. Goryd." % (bookingId, ownerPhone)
    send_sms(phoneNumber, msg)

def send_on_booking_approval(phoneNumber, customerName, bookingId, tripStartDate, tripStartTime, tripEndDate, tripEndTime, carDetails, rent, paymentStatus, mapLink):
    msg = "Dear %s, your booking id %s has been approved.\nBooking ID: %s\nYour trip starts at: %s at %s\nYour trip ends at: %s at %s\nCar details: %s\nTotal rent: %s\nPayment status: %s\nMap link: %s\nWe will provide you the owner's contact number 6 hours before your trip begins. Please carry your driving license with you while picking your car. For help please call us at +91-9930467093." % (customerName, bookingId, bookingId, tripStartDate, tripStartTime, carDetails, rent, paymentStatus, mapLink)
    send_sms(phoneNumber, msg)

def send_reminder_sms_to_customer(phoneNumber, customerName, bookingId, ownerMobile, loc):
    msg = "Dear %s, this is a gentle reminder with reference to your booking id %s. The owner's contact number is %s. \n Follow the link below to get the directions: https://www.google.com/maps/place/%s,%s\n. Please carry your driving license with you while picking your car. For help please call us at +91-9930467093." % (customerName, bookingId, ownerMobile, loc[0], loc[1])
    send_sms(phoneNumber, msg)
