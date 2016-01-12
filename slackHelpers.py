from httpHelpers import *
from config import *
import json

def sendToSlack(url, text, icon_url = None, icon_emoji = None):
	data = {}
	data["text"] = text
	if icon_url:
		data["icon_url"] = icon_url
	if icon_emoji:
		data["icon_emoji"] = icon_emoji
	response = openUrl(url, json.dumps(data), headers = {"Content-type": "application/json"})

	return response

def buildSlackStringFromTrain(train):
	if train["isPrimroseHill"]:
		lineStatus = "On our line "
	else:
		lineStatus = "NOT on our line "

	slackString =  "\n +++++++ \n" + lineStatus + "\n" + train["PlanDep"] + " (" + train["ActDep"] + ")" + "\n " + \
					train["Origin"] +  " -> " + train["Destination"] + ".\n " + \
					"Its ID is " + "<" + RTTBASEURL + train["IDLink"] + "|" + train["ID"] +">" + "\n +++++++ \n"
	return slackString