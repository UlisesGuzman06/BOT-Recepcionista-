from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/reply_whatsapp", methods=['POST'])
def reply_whatsapp():
	# Create a new Twilio MessagingResponse
	resp = MessagingResponse()
	resp.message("Message received! Hello again from the Twilio Sandbox for WhatsApp.")

	# Return the TwiML (as XML) response
	return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
	app.run(port=3500)