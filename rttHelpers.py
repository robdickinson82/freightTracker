from httpHelpers import *
from config import *

def openRTTUrl(location, stp, show, order):
	response = openUrl(RTTBASEURL + "/search/advanced/" +
		location +
		"?" + 
		"stp=" + stp + "&" + 
		"show=" + show + "&" +
		"order=" + order)
	html = response.read()
	return html

def openRTTUrl_CMDNRDJ_AroundNow(): 
	location = "CMDNRDJ"
	stp = "WVS"
	show ="freight"
	order = "wtt"
	html =  openRTTUrl(location, stp, show, order)
	return html

def openRTTUrl_Test():
	response = openUrl(RTTBASEURL + "/search/advanced/CMDNRDJ/2016/01/15/0000-2359?stp=WVS&show=freight&order=wtt")
	html = response.read()
	return html	

def openRTTUrl_TrainDetail(link):
	response = openUrl(RTTBASEURL + link)
	html = response.read()
	return html
