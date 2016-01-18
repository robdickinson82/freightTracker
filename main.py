# -*- coding: utf-8 -*-
from config import *

import re
import time
import sys

from rttHelpers import *
from bsHelpers import *
from slackHelpers import *
from trainHelpers import *

def extractTrainsFromSoup(docSoup, trains):
	print("Getting Trains...")
	resultsTable = docSoup.find(class_="servicelist")
	if resultsTable:
		resultsRows = resultsTable.findAll("tr")
	else:
		resultsRows = []
	if resultsRows:
		for resultsRow in resultsRows:
			
			train = {}
			resultsTds = resultsRow.findAll("td")
			if resultsTds:
				print("... Getting Train")
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
				#train["isPrimroseHill"] = isPrimroseHillTrain(train)
				getTrainDetails(train)
				trains.append(train)
				
				print ("...... Got Train " + train["ID"])
				sys.stdout.flush()
	return (trains)

def getTrainDetails(train):
	trainDetailSoup = getTrainDetailSoup(train)
	getTrainSummaryDetailsFromSoup(train, trainDetailSoup)
	getTrainTimetableFromSoup(train, trainDetailSoup)
	return

def getTrainTimetableFromSoup(train, trainDetailSoup):
	timetableSoup = trainDetailSoup.find("table", class_="advanced")
	timetableRowsSoups = timetableSoup.tbody.findAll("tr")

	train["Stops"] = {}
	train["Stops"]["List"] = []
	train["Stops"]["Lookup"] = {}
	stopNum = 0
	for timetableRowsSoup in timetableRowsSoups:

		stop = {}
		stop["passCall"] = timetableRowsSoup["class"][0]
		stop["Type"] = timetableRowsSoup["class"][1]

		extractingCells = [
							"platform",
							"line",
							"path",
							"engineering",
							"pathing",
							"performance"
		]

		for extractingCell in extractingCells:
			cellToProperty(timetableRowsSoup, stop, extractingCell)
	
		locationCell = timetableRowsSoup.find("td", class_="location")
		stop["Name"] = locationCell.span.a.string
		stop["Link"] = locationCell.span.a["href"]

		plannedCells = None
		plannedCells = timetableRowsSoup.findAll("td", class_=re.compile("wtt"))
		if plannedCells:
			stop["PlanArr"] = plannedCells[0].string
			stop["PlanDep"] = plannedCells[1].string

		actualCells = None
		actualCells = timetableRowsSoup.findAll("td", class_=re.compile("realtime"))
		if actualCells and len(actualCells) > 1:
			stop["ActArr"] = actualCells[0].string
			stop["ActDep"] = actualCells[1].string

		train["Stops"]["List"].append(stop)

		if train["Stops"]["Lookup"].has_key(stop["Name"]):
			train["Stops"]["Lookup"][stop["Name"]].append(stopNum)
		else:
			train["Stops"]["Lookup"][stop["Name"]] = [stopNum]

		stopNum = stopNum + 1

	return

def getTrainSummaryDetailsFromSoup(train, trainDetailSoup):
	detailsTableSoup = trainDetailSoup.find("div", class_="detailed-schedule-info")
	detailsDivsSoups = detailsTableSoup.div.findAll("div")
	detailsSoups = detailsTableSoup.div.findAll("strong")

	if len(detailsDivsSoups) > 0:
		scheduleDetailsStrongs = detailsDivsSoups[0].findAll("strong")
		train["ScheduleInfo"] = {}
		train["ScheduleInfo"]["Timetable"] = scheduleDetailsStrongs[0].string
		train["ScheduleInfo"]["ScheduleUID"] = scheduleDetailsStrongs[1].string
		if len(scheduleDetailsStrongs) == 4:
			train["ScheduleInfo"]["RunType"] = None
			train["ScheduleInfo"]["RunFrom"] = scheduleDetailsStrongs[2].string
			train["ScheduleInfo"]["RunEnd"] = scheduleDetailsStrongs[2].string
			train["ScheduleInfo"]["ServiceCode"] = scheduleDetailsStrongs[3].string
		elif len(scheduleDetailsStrongs) == 6:
			train["ScheduleInfo"]["RunType"] = scheduleDetailsStrongs[2].string
			train["ScheduleInfo"]["RunFrom"] = scheduleDetailsStrongs[3].string
			train["ScheduleInfo"]["RunEnd"] = scheduleDetailsStrongs[4].string
			train["ScheduleInfo"]["ServiceCode"] = scheduleDetailsStrongs[5].string	
		else: 
			train["ScheduleInfo"]["RunType"] = None
			train["ScheduleInfo"]["RunFrom"] = None
			train["ScheduleInfo"]["RunEnd"] = None
			train["ScheduleInfo"]["ServiceCode"] = None

	if len(detailsDivsSoups) > 1:
		operationalDetailsStrongs = detailsDivsSoups[1].findAll("strong")

		train["OperationalInfo"] = {}
		train["OperationalInfo"]["ScheduleFrom"] = operationalDetailsStrongs[0].string
		train["OperationalInfo"]["MaxSpeed"] = operationalDetailsStrongs[1].string
		if len(operationalDetailsStrongs) == 3:
			train["OperationalInfo"]["PowerType"] = operationalDetailsStrongs[2].string
			train["OperationalInfo"]["Weight"] = None
		elif len(operationalDetailsStrongs) == 4:
			train["OperationalInfo"]["PowerType"] = operationalDetailsStrongs[2].string
			train["OperationalInfo"]["Weight"] = operationalDetailsStrongs[3].string
		else: 
			train["OperationalInfo"]["PowerType"] = None
			train["OperationalInfo"]["Weight"] = None

	#  This is commented out as passenger trains break it.  We do not need it.

	#if len(detailsDivsSoups) > 2:
		#statusDetailsStrongs = detailsDivsSoups[2].findAll("strong")

		#train["StatusInfo"] = {}
		#train["StatusInfo"]["TrustId"] = statusDetailsStrongs[0].string
		#train["StatusInfo"]["RunningID"] = statusDetailsStrongs[1].string
		#train["StatusInfo"]["Activated"] = statusDetailsStrongs[2].string

	return

def getTrainsForAroundNowAtCMDRDJ():
	trains = []
	if DEBUG:
		htmlDoc = openRTTUrl_Test()
	else:
		htmlDoc = openRTTUrl_CMDNRDJ_AroundNow()
	
	docSoup = getSoupFromHtml(htmlDoc)
	
	trains = extractTrainsFromSoup(docSoup, trains)
	
	return trains

def getTrainDetailSoup(train):
	htmlDoc = openRTTUrl_TrainDetail(train["IDLink"])
	docSoup = getSoupFromHtml(htmlDoc)
	#print(docSoup.prettify().encode('utf-8'))
	return docSoup

print ("+++++++ Starting Loop +++++++")
rc = sendStartupMessageToSlack()

while True:
	print (NotifiedTrains)
	print("Getting Train Times...")
	trains = getTrainsForAroundNowAtCMDRDJ()
		
	if trains:
		print("Got Train Times")
		for train in trains:
			print (u".. Checking Train " + train["ID"] + u" " + train["Origin"] + u"->" + train["Destination"] + u" due ")
			if trainNotCancelled(train):				
				print (".... Train Not Cancelled")
				if isPrimroseHillTrain(train):
					print (".... Train on our Line")
					direction = getTrainDirection(train)
					if (direction):
						print (".... Train is heading " + direction)
					else: 
						print (".... This is odd - Primrose Hill is not in the right place any more")
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
					print(".... Train not on our line")
			else:
				print (".... Train Cancelled")
	else:
		print("No Train Times")
	sys.stdout.flush()
	time.sleep(60)