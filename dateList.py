import os
import time

# get script location, and dao folder
__location__ = os.path.dirname(os.path.abspath(__file__))
daoDir = os.path.join(__location__, "dao")

# create dao folder if it does not exist
if not os.path.isdir(daoDir):
	os.makedirs(daoDir)
	
# open the output file
f = open('dateList.csv', 'w')

#get all files in dao folder
for root, dirs, files in os.walk(daoDir):
	for file in files:
		filePathFull = os.path.join(root, file)
		filePath = os.path.join(root, file).split(daoDir)[1]
		if filePath.startswith("\\"):
			filePath = filePath[1:]
		if filePath.startswith("/"):
			filePath = filePath[1:]
		print ("writing " + filePath)
		
		timeList = []
		today = time.strftime("%Y-%m-%d")
		
		mtime = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(filePathFull)))
		atime = time.strftime('%Y-%m-%d', time.gmtime(os.path.getatime(filePathFull)))
		ctime = time.strftime('%Y-%m-%d', time.gmtime(os.path.getctime(filePathFull)))
		if not mtime in timeList:
			if not mtime == today:
				timeList.append(mtime)
		if not atime in timeList:
			if not atime == today:
				timeList.append(atime)
		if not ctime in timeList:
			if not ctime == today:
				timeList.append(ctime)
		
		fixedDate = ""
		for sortDate in sorted(timeList):
			fixedDate = fixedDate + "||\"=\"\"" + sortDate + "\"\"\""
		
		f.write(filePath + fixedDate +" \n")
		
# close the output file
f.close()