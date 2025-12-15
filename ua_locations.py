"""
University Archives location utilities.
Handles conversion of local location coordinate systems to ArchivesSpace location records.
"""

def main_shelf(coordinates):
    """Parse main storage shelf coordinates"""
    coord_list = {
        "Building": "",
        "Floor": "",
        "Room": "",
        "Area": "",
        "Label1": "",
        "Place1": "",
        "Label2": "",
        "Place2": "",
        "Label3": "",
        "Place3": "",
        "Title": "",
        "Note": ""
    }
    
    if len(coordinates.split("-")) != 4:
        print(f"Error, shelf is in main storage, but is incorrect: {coordinates}")
    else:
        if coordinates.lower().strip().startswith("sb17"):
            coord_list["Building"] = "Main Library"
            coord_list["Floor"] = "Basement"
            coord_list["Room"] = "SB17"
            coord_list["Title"] = f"Main Library, Basement, SB17 [Row: {coordinates.split('-')[1]}, Bay: {coordinates.split('-')[2]}, Shelf: {coordinates.split('-')[3]}]"
        elif coordinates.lower().strip().startswith("sb14"):
            coord_list["Building"] = "Main Library"
            coord_list["Floor"] = "Basement"
            coord_list["Room"] = "SB14"
            coord_list["Title"] = f"Main Library, Basement, SB14 [Row: {coordinates.split('-')[1]}, Bay: {coordinates.split('-')[2]}, Shelf: {coordinates.split('-')[3]}]"
        else:
            coord_list["Building"] = "Science Library"
            coord_list["Floor"] = "3"
            coord_list["Room"] = "Main Storage"
            coord_list["Area"] = coordinates.split("-")[0]
            coord_list["Title"] = f"Science Library, 3, Main Storage, {coordinates.split('-')[0]} [Row: {coordinates.split('-')[1]}, Bay: {coordinates.split('-')[2]}, Shelf: {coordinates.split('-')[3]}]"
            
        coord_list["Label1"] = "Row"
        coord_list["Place1"] = coordinates.split("-")[1]
        coord_list["Label2"] = "Bay"
        coord_list["Place2"] = coordinates.split("-")[2]
        coord_list["Label3"] = "Shelf"
        coord_list["Place3"] = coordinates.split("-")[3]
        
    return coord_list


def location_to_aspace(coordinates, note=None):
    """
    Convert local coordinate notation to ArchivesSpace location format.
    Returns tuple: (location_data, is_range)
    """
    main_areas = ["A", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
    
    coord_list = {
        "Building": "",
        "Floor": "",
        "Room": "",
        "Area": "",
        "Label1": "",
        "Place1": "",
        "Label2": "",
        "Place2": "",
        "Label3": "",
        "Place3": "",
        "Title": "",
        "Note": ""
    }
    
    # Check if single or range
    if "/" in coordinates:
        is_range = True
        total_list = []
        if "SB17" in coordinates or "SB14" in coordinates:
            high_shelf = 8
        else:
            high_shelf = 9
        
        coord1, coord2_note = coordinates.split("/")
        if "(" in coord2_note:
            coord2 = coord2_note.split("(")[0].strip()
            note = coord2_note.split("(")[1].replace(")", "").strip()
        else:
            coord2 = coord2_note.strip()
        
        # Parse range endpoints
        parts1 = coord1.split("-")
        parts2 = coord2.split("-")
        
        # Generate all locations in range
        if len(parts1) == 4 and len(parts2) == 4:
            area = parts1[0]
            row_start = int(parts1[1])
            row_end = int(parts2[1])
            bay_start = int(parts1[2])
            bay_end = int(parts2[2])
            shelf_start = int(parts1[3])
            shelf_end = int(parts2[3])
            
            for row in range(row_start, row_end + 1):
                for bay in range(bay_start, bay_end + 1):
                    for shelf in range(shelf_start, min(shelf_end + 1, high_shelf + 1)):
                        loc = main_shelf(f"{area}-{row}-{bay}-{shelf}")
                        if note:
                            loc["Note"] = note
                        total_list.append(loc)
        
        return (total_list, True)
    else:
        # Single location
        is_range = False
        coord_list = main_shelf(coordinates)
        if note:
            coord_list["Note"] = note
        return (coord_list, False)


def find_location_uri(client, loc_title):
    """
    Search for a location by title and return its URI.
    """
    try:
        search_results = client.get('/search', params={
            'page': '1',
            'page_size': '100',
            'q': f'"{loc_title}"'
        }).json()
        
        for result in search_results.get('results', []):
            if result.get('title', '').strip().lower() == loc_title.strip().lower():
                return result.get('uri')
        
        print(f"WARNING: Could not find location: {loc_title}")
        return None
    except Exception as e:
        print(f"Error searching for location {loc_title}: {e}")
        return None
