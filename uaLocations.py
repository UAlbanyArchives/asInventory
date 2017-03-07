
def mainShelf(coordinates):
	coordList = {"Building": "", "Floor": "", "Room": "", "Area": "", "Label1": "", "Place1": "", "Label2": "", "Place2": "", "Label3": "", "Place3": "", "Title": "", "Note": ""}
	if not len(coordinates.split("-")) == 4:
		print ("Error, shelf is in main stacks, but is incorrect")
	else:
		coordList["Building"] = "Science Library"
		coordList["Floor"] = "3"
		coordList["Room"] = "Main Stacks"
		coordList["Area"] = coordinates.split("-")[0]
		coordList["Label1"] = "Row"
		coordList["Place1"] = coordinates.split("-")[1]
		coordList["Label2"] = "Bay"
		coordList["Place2"] = coordinates.split("-")[2]
		coordList["Label3"] = "Shelf"
		coordList["Place3"] = coordinates.split("-")[3]
		coordList["Title"] = "Science Library, 3, Main Stacks, " + coordinates.split("-")[0] + " [Row: " + coordinates.split("-")[1] + ", Bay: " + coordinates.split("-")[2] + ", Shelf: " + coordinates.split("-")[3] + "]"
	return coordList

def test2():
	print "elloe world!"
	
def location2ASpace(coordinates, note = None):

	mainAreas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
	
	coordList = {"Building": "", "Floor": "", "Room": "", "Area": "", "Label1": "", "Place1": "", "Label2": "", "Place2": "", "Label3": "", "Place3": "", "Title": "", "Note": ""}
	
	#check if single or range
	if "/" in coordinates:
	
		isRange = True
		totalList = []
		coord1, coord2 = coordinates.split("/")
		if coord1.split("-")[2] == coord2.split("-")[2]:
			shelf1 = int(coord1.split("-")[3])
			shelf2 = int(coord2.split("-")[3])
			for shelf in range(shelf1, shelf2 + 1):
				coordList = mainShelf(coord1[:6] + str(shelf))
				totalList.append(coordList)
			coordList = totalList
		else:
			coordStart = coordinates[:4]
			bay1 = int(coord1[4])
			bay2 = int(coord2[4])
			shelf1 = int(coord1[6])
			shelf2 = int(coord2[6])
			for bay in range(bay1, bay2 + 1):
				if bay == bay1:
					for shelf in range(shelf1, 9):
						coordList = mainShelf(coordStart + str(bay) + "-" + str(shelf))
						totalList.append(coordList)
				elif bay == bay2:
					for shelf in range(1, shelf2 + 1):
						coordList = mainShelf(coordStart + str(bay) + "-" + str(shelf))
						totalList.append(coordList)
				else:
					for shelf in range(1, 9):
						coordList = mainShelf(coordStart + str(bay) + "-" + str(shelf))
						totalList.append(coordList)
			coordList = totalList
	
	else:
		#single shelf
		isRange = False
		
		if not note is None:
			coordList["Note"] = note
		
		#check if in main stacks
		area = coordinates.split("-")[0]
		if area in mainAreas:
			#check if correct
			
			coordList = mainShelf(coordinates)
				
		elif coordinates.lower().startswith("rr"):
		
			coordList["Building"] = "Science Library"
			coordList["Floor"] = "3"
			coordList["Room"] = "Reading Room"
			coordList["Label1"] = "Shelf"
			coordList["Place1"] = coordinates.split("RR")[1]
			coordList["Title"] = "Science Library, 3, Reading Room [Shelf: " + coordinates.split("RR")[1] + "]"	
		
		elif coordinates.lower().startswith("ccbe"):
			#check if correct
			if not len(coordinates.split("-")) == 2:
				print ("Error, shelf is in CCBE, but is incorrect")
			else:
				coordList["Building"] = "Science Library"
				coordList["Floor"] = "LL"
				coordList["Room"] = "CCBE"
				coordList["Label1"] = "Row"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Title"] = "Science Library, LL, CCBE, [Row: " + coordinates.split("-")[1] + "]"
		
		elif coordinates.lower().startswith("sb"):
		
			coordList["Building"] = "Main Library"
			coordList["Floor"] = "Basement"			
			coordList["Room"] = coordinates[:4].upper()
			
			if len(coordinates) == 4:
				coordList["Label1"] = "Room"
				coordList["Place1"] = coordinates.upper()
				coordList["Title"] = "Main Library, Basement, " + coordinates.upper() + "[Room: " + coordinates.upper() + "]"
			elif len(coordinates) == 10:
				coordList["Label1"] = "Row"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Label2"] = "Bay"
				coordList["Place2"] = coordinates.split("-")[2]
				coordList["Label3"] = "Shelf"
				coordList["Place3"] = coordinates.split("-")[3]
				coordList["Title"] = "Main Library, Basement, " + coordinates.split("-")[0] + " [Row: " + coordinates.split("-")[1] + ", Bay: " + coordinates.split("-")[2] + ", Shelf: " + coordinates.split("-")[3] + "]"
				
			
			else:
				print ("Error, shelf is in SB, but is incorrect")
				
		elif coordinates.split("-")[0] == "L":
		
			if not len(coordinates.split("-")) == 3:
				print ("Error, shelf is in main stacks, but is incorrect")
			else:
				coordList["Building"] = "Science Library"
				coordList["Floor"] = "3"
				coordList["Room"] = "Main Stacks"
				coordList["Area"] = coordinates.split("-")[0]
				coordList["Label1"] = "Bay"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Label2"] = "Flat Storage"
				coordList["Place2"] = coordinates.split("-")[2]
				coordList["Title"] = "Science Library, 3, Main Stacks, " + coordinates.split("-")[0] + " [Bay: " + coordinates.split("-")[1] + ", Flat Storage: " + coordinates.split("-")[2] + "]"				
			
		elif coordinates.lower().startswith("cold"):
			coordList["Building"] = "Science Library"
			coordList["Floor"] = "3"
			coordList["Room"] = "Cold Room"
			if len(coordinates.split("-")) == 1:
				coordList["Label1"] = "Room"
				coordList["Place1"] = "Cold"
				coordList["Title"] = "Science Library, 3, Cold Room [Room: Cold]"
			if len(coordinates.split("-")) == 3:
				coordList["Label1"] = "Bay"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Label2"] = "Shelf"
				coordList["Place2"] = coordinates.split("-")[2]
				coordList["Title"] = 	"Science Library, 3, Cold Room [Bay: " + coordinates.split("-")[1] + ", Shelf: " + coordinates.split("-")[2] + "]"
			elif len(coordinates.split("-")) == 4:
				coordList["Label1"] = "Cabinet"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Label2"] = "Drawer"
				coordList["Place2"] = coordinates.split("-")[2]
				coordList["Label3"] = "Section"
				coordList["Place3"] = coordinates.split("-")[3]
				coordList["Title"] = "Science Library, 3, Cold Room [Cabinet: " + coordinates.split("-")[1] + ", Drawer: " + coordinates.split("-")[2] + ", Section: " + coordinates.split("-")[3] + "]"
			
			else:
				print ("Error, shelf is in cold room, but is incorrect")	
		
		
		elif coordinates.lower().startswith("v"):
			coordList["Building"] = "Science Library"
			coordList["Floor"] = "3"
			coordList["Room"] = "Vault"
			coordList["Area"] = "V"
			if len(coordinates.split("-")) == 1:
				coordList["Label1"] = "Room"
				coordList["Place1"] = "Vault"
				coordList["Title"] = "Science Library, 3, Vault [Room: Vault]"
			elif len(coordinates.split("-")) == 4:
				coordList["Label1"] = "Row"
				coordList["Place1"] = coordinates.split("-")[1]
				coordList["Label2"] = "Bay"
				coordList["Place2"] = coordinates.split("-")[2]
				coordList["Label3"] = "Shelf"
				coordList["Place3"] = coordinates.split("-")[3]
				coordList["Title"] = "Science Library, 3, Vault, V [Row: " + coordinates.split("-")[1] + ", Bay: " + coordinates.split("-")[2] + ", Shelf: " + coordinates.split("-")[3] + "]" 
			elif len(coordinates.split("-")) == 5:
				coordList["Label1"] = "Row"
				coordList["Place1"] = coordinates.split("-")[2]
				coordList["Label2"] = "Bay"
				coordList["Place2"] = coordinates.split("-")[3]
				coordList["Label3"] = "Shelf"
				coordList["Place3"] = coordinates.split("-")[4]
				coordList["Title"] = "Science Library, 3, Vault, V [Row: " + coordinates.split("-")[2] + ", Bay: " + coordinates.split("-")[3] + ", Shelf: " + coordinates.split("-")[4] + "]" 
			else:
				print ("Error, shelf is in vault, but is incorrect")	
			
		
	return coordList, isRange