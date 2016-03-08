# -*- coding: utf-8 -*-
from config import *

import re
import time
import sys

from rttHelpers import *
from bsHelpers import *
from slackHelpers import *

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
	if train["ActDep"] == "(Q)" or train["ActDep"] == "Cancel" or train["ActDep"] == "N/R":
		notCancelled = False
	return notCancelled

def isPrimroseHillTrain(train):
	if train["Stops"]["Lookup"].has_key("Primrose Hill [PRM]"):
		result = True
	else:
		result = False
	return result

def checkSpecialTrain(train, specialWords):
	specialTrain = []

	for specialWord in specialWords:
		if " " + specialWord + " " in train["Origin"] or " " + specialWord + " " in train["Destination"]:
			specialTrain.append(specialWord)	
	return specialTrain

def getTrainDirection(train):
	
	northbound = False
	southbound = False

	if train["Stops"]["Lookup"].has_key("Camden Road Jn"):
		cmdRdStops = train["Stops"]["Lookup"]["Camden Road Jn"]
		if train["Stops"]["Lookup"].has_key("Primrose Hill [PRM]"):
			phStops = train["Stops"]["Lookup"]["Primrose Hill [PRM]"]
			for cmdRdStop in cmdRdStops:
				for phStop in phStops:
					diff = cmdRdStop - phStop
					if diff == 1:
						southbound = True
					elif diff == -1:
						northbound = True
	result = None
	if northbound:
		if southbound:
			result = "Both"
		else:
			result = "West"
	else:
		if southbound:
			result = "East"
		else:
			result = None

	return result

def trainWithinNotificationThreshold(train):
	withinThreshold = False

	direction = getTrainDirection(train)

	if direction == "West":
		departureTime = train["ActDep"]
		minsToTrain = minutesToTime(departureTime) + WESTBOUND_LAG
		if  minsToTrain <= NOTIFICATION_THRESHOLD:
			withinThreshold = True
	elif direction == "East":
		## This is bugged if the train passes us twice
		#print(train["Stops"]["List"][train["Stops"]["Lookup"]["Camden Jn"][0]])
		#print(train["Stops"]["List"])
		if train["Stops"]["List"][train["Stops"]["Lookup"]["Primrose Hill [PRM]"][0]].has_key("ActDep"):
			departureTime = train["Stops"]["List"][train["Stops"]["Lookup"]["Primrose Hill [PRM]"][0]]["ActDep"]
			lag = PH_TO_IC_LAG
			print("Got PH dep time")
		elif train["Stops"]["List"][train["Stops"]["Lookup"]["Camden Jn"][0]].has_key("ActDep"):
			departureTime = train["Stops"]["List"][train["Stops"]["Lookup"]["Camden Jn"][0]]["ActDep"]
			lag = PH_TO_IC_LAG + CJ_TO_PH_DIFF
			print("Got CJ dep time")
		elif train["ActDep"]:
			departureTime = train["ActDep"]
			lag = PH_TO_IC_LAG + CJ_TO_PH_DIFF
			print("Got trains own dep time")
		else:
			print("ERROR: No departure time...")
			departureTime = None
		if departureTime:	
			minsToTrain = minutesToTime(departureTime) + lag
			if minsToTrain <= NOTIFICATION_THRESHOLD:
				withinThreshold = True

	return withinThreshold


NotifiedTrains = {}
def notAlreadyNotified(train):
	trainId = train["ScheduleInfo"]["ScheduleUID"] + (time.strftime("%Y%d%m"))
	notNotifiedAlready = True
	if NotifiedTrains.has_key(trainId):
		notNotifiedAlready = False
	return notNotifiedAlready

def cellToProperty(timetableRowsSoup, stop, className):
	cell = timetableRowsSoup.find("td", class_=className)
	if cell:
		stop[className.title()] = cell.string	
	else:
		stop[className.upper()] = None

	return