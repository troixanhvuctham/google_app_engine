import json
import random
import sqlite3
import requests
import json
from pprint import pprint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('mobileshop-cca5d-firebase-adminsdk-0wlzq-b6d07b693f.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mobileshop-cca5d.firebaseio.com/',
})

from http.client import HTTPException
from urllib.error import HTTPError, URLError

from flask import Flask, jsonify, make_response, request
from googleapiclient.discovery import build


app = Flask(__name__)
log = app.logger
thanks = ['You\'re welcome!', 'Not at all', 'Glad to help you', 'Don\'t mention it.', 'My pleasure.']
suggestion = ["You want IOS or Android smartphone?", "Give me the price, then i will recommend for you"]

with open('data.json') as f:
    data = json.load(f)
#data = db.reference('/').get()
os = data["os"]
#price = data["price"]
#pprint(data)
#pprint(os)
#pprint(price)
#--------user data
OS = ''
#message = [ { "card": { "title": "Title: this is a card title","subtitle": "This is the body text of a card.  You can even use line\n  breaks and emoji! 💁", "imageUri": "https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png",  "buttons": [  { "text": "This is a button", "postback": "https://assistant.google.com/" }]}},{"quickReplies": { "quickReplies": [ "Quick Reply", "Suggestion" ]  } }]
@app.route('/webhook', methods=['POST'])
def webhook():
	global OS
	# Get request parameters
	req = request.get_json(force=True)
	action = req.get('queryResult').get('action')
	s = req['queryResult']['queryText'];
	print(action)
	# Check if the request is for the translate action
	if action == 'ask.suggestion':
		#message = random.choice(suggestion)
		#res = {'fulfillmentText': message}
		res = {'fulfillmentMessages': message}
	elif action == 'os.suggestion':
		message = 'I have some recommend for you: '
		platform = req.get('queryResult').get('parameters').get("platform")
		OS = platform
		for m in os[platform]:
			for n in data[m]:
				message = message + n["name"] + ',\n'
		res = {'fulfillmentText': message}
	elif action == 'price.suggestion':
		message = 'I think these suit for you: '
		priced = checkPriceValue(req)
		flag = False
		print(priced)
		if int(priced) > 0:
			if OS:
				for m in os[OS]:
					for n in data[m]:
						if n["price"] >= priced - 200 and n["price"] <= priced + 200:
							flag = True
							message = message + n["name"] + ': ' + str(n["price"]) + '$,\n'
			else:
				for o in data["allos"]:
					for m in os[o]:
						for n in data[m]:
							if n["price"] >= priced - 200 and n["price"] <= priced + 200:
								flag = True
								message = message + n["name"] + ': ' + str(n["price"]) + '$,\n'
			if flag == False:
				message = 'Sorry, I can not find the right price for you.\n here are some another recommend: '
				for n in data['hottrend']:
					message = message + n["name"] + ': ' + str(n["price"]) + '$,\n'
		else:
			message = "Please give me the price you want."
		res = {'fulfillmentText': message}
	elif action == 'thanks':
		message = random.choice(thanks)
		OS = ''
		res = {'fulfillmentText': message}
	else:
		res = {'fulfillmentText': "greeting from server"}
	return make_response(jsonify(res))

def checkPriceValue(req):
	priced = -1
	try:
		priced = req.get('queryResult').get('parameters').get("number")
		if not priced:
			priced = req.get('queryResult').get('parameters').get("unit-currency").get("amount")
	except:
		priced = -1;
		print("An exception occurred with price!")
		return priced
	return priced

if __name__ == '__main__':
	PORT = 8080

	app.run(
		debug=True,
		port=PORT,
		host='0.0.0.0'
	)
