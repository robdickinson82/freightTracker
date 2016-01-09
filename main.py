# -*- coding: utf-8 -*-
from config import *

import re
import time
import sys

from rttHelpers import *
from bsHelpers import *
from slackHelpers import *

##bcec8309-9020-4b90-9870-057ba48a73a1 - Rail feed

def extractTrainsFromSoup(docSoup):
	resultsTable = docSoup.find(class_="servicelist")
	resultsRows = resultsTable.findAll("tr")

	trains = []
	for resultsRow in resultsRows:
		train = {}
		resultsTds = resultsRow.findAll("td")
		if resultsTds:
			train["Ind"] = resultsTds[0].string
			train["PlanArr"] = resultsTds[1].string
			train["ActArr"] = resultsTds[2].string
			train["Origin"] = resultsTds[3].span.string
			train["PI"] = resultsTds[4].string
			train["ID"] = resultsTds[5].string
			train["IDLink"] = resultsTds[5].a["href"]
			train["TOC"] = resultsTds[6].string
			train["Destination"] = resultsTds[7].span.string
			train["PlanDep"] = resultsTds[8].string	
			train["ActDep"] = resultsTds[9].string
			trains.append(train)
	return (trains)

def getTrainsForAroundNowAtCMDRDJ():
	htmlDoc = openRTTUrl_CMDNRDJ_AroundNow()
	docSoup = getSoupFromHtml(htmlDoc)
	trains = extractTrainsFromSoup(docSoup)
	return trains

def sendTrainToSlack(train):
	slackText = buildSlackStringFromTrain(train)
	response = sendToSlack(SLACKHOOK, slackText, icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response

def sendStartupMessageToSlack():
	response = sendToSlack(SLACKHOOK, "Starting monitoring script", icon_url = "https://slack.com/img/icons/app-57.png", icon_emoji = None)
	return response	

def minutesToTime(textTime):
	## Assumption is that both trains are in same day - will be broken around midnight bit we can fix later
	timeRE = re.compile("(?P<hour>\d\d)(?P<minute>\d\d)(.)?")
	m = re.match(timeRE, textTime)
	textTimeHour = int(m.groupdict()["hour"])
	textTimeMinute = int(m.groupdict()["minute"])
	currentTime = time.localtime()
	currentTimeHour = int(currentTime.tm_hour)
	currentTimeMinute = int(currentTime.tm_min)
	return (textTimeHour * 60.0 + textTimeMinute - currentTimeHour * 60.0 - currentTimeMinute)

def trainNotCancelled(train):
	notCancelled = True
	if train["ActDep"] == "(Q)" or train["ActDep"] == "Cancel":
		notCancelled = False
	return notCancelled

def trainWithinNotificationThreshold(train):
	withinThreshold = False
	minsToTrain = minutesToTime(train["ActDep"])
	if minsToTrain > -2.0 and minsToTrain <= NOTIFICATION_THRESHOLD:
		withinThreshold = True
	return withinThreshold

def notAlreadyNotified(train):
	trainId = train["ID"]
	notNotifiedAlready = True
	if NotifiedTrains.has_key(trainId):
		notNotifiedAlready = False
	return notNotifiedAlready

NotifiedTrains = {}
print ("+++++++ Starting Loop +++++++")
rc = sendStartupMessageToSlack()
while True:
	print (NotifiedTrains)
	print("Getting Train Times...")
	trains = getTrainsForAroundNowAtCMDRDJ()
	print("Got Train Times")
	if trains:
		for train in trains:
			print (u".. Checking Train " + train["ID"] + u" " + train["Origin"] + u"->" + train["Destination"] + u" due " + train["ActDep"].encode('utf-8'))
			if trainNotCancelled(train):
				print (".... Train Not Cancelled")
				if trainWithinNotificationThreshold(train):
					print (".... Train in scope")
					if notAlreadyNotified(train):
						print (".... Train not aleady notified")
						print (".... NOTIFYING")
						sendTrainToSlack(train)
						NotifiedTrains[train["ID"]] = train["ID"]
					else:
						print (".... Train already notified")
				else:
					print (".... Train not in scope - too early or late")
			else:
				print (".... Train Cancelled")
		sys.stdout.flush()
		time.sleep(60)