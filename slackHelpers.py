from httpHelpers import *
from config import *
import json

from trainHelpers import *

def sendToSlack(url, text, icon_url = None, icon_emoji = None):
	data = {}
	data["text"] = text
	if icon_url:
		data["icon_url"] = icon_url
	if icon_emoji:
		data["icon_emoji"] = icon_emoji

	if DEBUG:
		print (text.encode('utf-8'))
		response = 200
	else:
		response = openUrl(url, json.dumps(data), headers = {"Content-type": "application/json"})

	return response

def buildSlackStringFromTrain(train):

	specialTrains = checkSpecialTrain(train, ["Car", "Mail"])

	if len(specialTrains) > 0:
		string = ""
		for specialTrain in specialTrains:
			string = specialTrain + ", "
		specialTrainString = "\n SPECIAL TRAIN: " + string
	else:
		specialTrainString = ""

	slackString =  "\n +++++++ " + \
					specialTrainString + \
					"\n Train due heading " + getTrainDirection(train) + \
					"\n Planned: " + train["PlanDep"] + " (Actual: " + train["ActDep"] + ")" + "\n " + \
					train["Origin"] +  " -> " + train["Destination"] + ".\n " + \
					"Its ID is " + "<" + RTTBASEURL + train["IDLink"] + "|" + train["ID"] +">" + "\n +++++++ \n"
	return slackString

def sendTrainToSlack(train):
	slackText = buildSlackStringFromTrain(train)
	response = sendToSlack(SLACKHOOK, slackText, icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response

def sendStartupMessageToSlack():
	response = sendToSlack(SLACKHOOK, "Starting monitoring script", icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response	

def sendErrorMessageToSlack():
	response = sendToSlack(SLACKHOOK, "Something went wrong retrying...", icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response	

def sendTerminatingMessageToSlack():
	response = sendToSlack(SLACKHOOK, "Too many errors monitoring script is closing...", icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response	