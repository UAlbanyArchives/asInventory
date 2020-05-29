#!/usr/bin/env python

#date conversion function
#Function to make DACS and Normal (ISO) dates from timestamp
def stamp2DACS(timestamp):
	calendar = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
	stamp = timestamp[:8]
	year = stamp[:4]
	month = stamp[4:6]
	day = stamp[-2:]
	normal = year + "-" + month + "-" + day
	if day.startswith("0"):
		day = day[-1:]
	dacs = year + " " + calendar[month] + " " + day
	return dacs, normal
	
def iso2DACS(normalDate):
	calendar = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
	if len(normalDate) < 1:
		displayDate = normalDate
	if "/" in normalDate:
		startDate = normalDate.split('/')[0]
		endDate = normalDate.split('/')[1]
		if "-" in startDate:
			if startDate.count('-') == 1:
				startYear = startDate.split("-")[0]
				startMonth = startDate.split("-")[1]
				displayStart = startYear + " " + calendar[startMonth]
			else:
				startYear = startDate.split("-")[0]
				startMonth = startDate.split("-")[1]
				startDay = startDate.split("-")[2]
				if startDay.startswith("0"):
					displayStartDay = startDay[1:]
				else:
					displayStartDay = startDay
				displayStart = startYear + " " + calendar[startMonth] + " " + displayStartDay
		else:
			displayStart = startDate
		if "-" in endDate:
			if endDate.count('-') == 1:
				endYear = endDate.split("-")[0]
				endMonth = endDate.split("-")[1]
				displayEnd = endYear + " " + calendar[endMonth]
			else:
				endYear = endDate.split("-")[0]
				endMonth = endDate.split("-")[1]
				endDay = endDate.split("-")[2]
				if endDay.startswith("0"):
					displayEndDay = endDay[1:]
				else:
					displayEndDay = endDay
				displayEnd = endYear + " " + calendar[endMonth] + " " + displayEndDay
		else:
			displayEnd = endDate
		displayDate = displayStart + "-" + displayEnd
	else:
		if "-" in normalDate:
			if normalDate.count('-') == 1:
				year = normalDate.split("-")[0]
				month = normalDate.split("-")[1]
				displayDate = year + " " + calendar[month]
			else:
				year = normalDate.split("-")[0]
				month = normalDate.split("-")[1]
				day = normalDate.split("-")[2]
				if day.startswith("0"):
					displayDay = day[1:]
				else:
					displayDay = day
				displayDate = year + " " + calendar[month] + " " + displayDay
		else:
			displayDate = normalDate
	return displayDate