import os

# get script location, and dao folder
__location__ = os.path.dirname(os.path.abspath(__file__))
daoDir = os.path.join(__location__, "dao")

# create dao folder if it does not exist
if not os.path.isdir(daoDir):
	os.makedirs(daoDir)
	
# open the output file
f = open('daoList.txt', 'w')

#get all files in dao folder
for root, dirs, files in os.walk(daoDir):
	for file in files:
		filePath = os.path.join(root, file).split(daoDir)[1]
		if filePath.startswith("\\"):
			filePath = filePath[1:]
		if filePath.startswith("/"):
			filePath = filePath[1:]
		print ("writing " + filePath)
		f.write(filePath + "\n")
		
# close the output file
f.close()