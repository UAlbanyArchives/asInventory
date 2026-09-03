"""
University Archives location utilities.
Handles conversion of local location coordinate systems to ArchivesSpace location records.
"""


def _norm(value):
    """Normalize a value for case-insensitive comparisons."""
    if value is None:
        return ""
    return str(value).strip().lower()

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
    
    parts = [part.strip() for part in coordinates.split("-")]

    if len(parts) == 2:
        # 2-part shorthand like "CCBE-105B"
        room = parts[0]
        row = parts[1]
        coord_list["Building"] = "Science Library"
        coord_list["Floor"] = "LL"
        coord_list["Room"] = room
        coord_list["Label1"] = "Row"
        coord_list["Place1"] = row
        coord_list["Title"] = f"Science Library, LL, {room} [Row: {row}]"
    elif len(parts) != 4:
        print(f"Error, shelf is in main storage, but is incorrect: {coordinates}")
    else:
        if coordinates.lower().strip().startswith("sb17"):
            coord_list["Building"] = "Main Library"
            coord_list["Floor"] = "Basement"
            coord_list["Room"] = "SB17"
            coord_list["Title"] = f"Main Library, Basement, SB17 [Row: {parts[1]}, Bay: {parts[2]}, Shelf: {parts[3]}]"
        elif coordinates.lower().strip().startswith("sb14"):
            coord_list["Building"] = "Main Library"
            coord_list["Floor"] = "Basement"
            coord_list["Room"] = "SB14"
            coord_list["Title"] = f"Main Library, Basement, SB14 [Row: {parts[1]}, Bay: {parts[2]}, Shelf: {parts[3]}]"
        else:
            coord_list["Building"] = "Science Library"
            coord_list["Floor"] = "3"
            coord_list["Room"] = "Main Storage"
            coord_list["Area"] = parts[0]
            coord_list["Title"] = f"Science Library, 3, Main Storage, {parts[0]} [Row: {parts[1]}, Bay: {parts[2]}, Shelf: {parts[3]}]"
            
        coord_list["Label1"] = "Row"
        coord_list["Place1"] = parts[1]
        coord_list["Label2"] = "Bay"
        coord_list["Place2"] = parts[2]
        coord_list["Label3"] = "Shelf"
        coord_list["Place3"] = parts[3]
        
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


def find_location_uri(client, loc_title, loc_data=None):
    """
    Search for a location by title and return its URI.
    """
    try:
        if loc_title and len(str(loc_title).strip()) > 0:
            search_results = client.get('/search', params={
                'page': '1',
                'page_size': '100',
                'q': f'"{loc_title}"'
            }).json()

            for result in search_results.get('results', []):
                if _norm(result.get('title', '')) == _norm(loc_title):
                    return result.get('uri')

        # Fallback for titles that don't exactly align with local shorthand:
        # match by explicit location fields (building/floor/room/row).
        if isinstance(loc_data, dict):
            required_pairs = [
                ('building', 'Building'),
                ('floor', 'Floor'),
                ('room', 'Room'),
                ('coordinate_1_label', 'Label1'),
                ('coordinate_1_indicator', 'Place1')
            ]
            optional_pairs = [
                ('area', 'Area'),
                ('coordinate_2_label', 'Label2'),
                ('coordinate_2_indicator', 'Place2'),
                ('coordinate_3_label', 'Label3'),
                ('coordinate_3_indicator', 'Place3')
            ]

            has_required = all(_norm(loc_data.get(local_key)) != "" for _, local_key in required_pairs)
            if has_required:
                ids_response = client.get('/locations', params={'all_ids': 'true'}).json()

                location_ids = []
                if isinstance(ids_response, list):
                    location_ids = ids_response
                elif isinstance(ids_response, dict):
                    if isinstance(ids_response.get('id_set'), list):
                        location_ids = ids_response.get('id_set', [])
                    elif isinstance(ids_response.get('results'), list):
                        for result in ids_response.get('results', []):
                            if isinstance(result, dict) and 'id' in result:
                                location_ids.append(result['id'])

                for loc_id in location_ids:
                    location_obj = client.get(f'/locations/{loc_id}').json()

                    matches_required = all(
                        _norm(location_obj.get(remote_key)) == _norm(loc_data.get(local_key))
                        for remote_key, local_key in required_pairs
                    )
                    if not matches_required:
                        continue

                    matches_optional = True
                    for remote_key, local_key in optional_pairs:
                        if _norm(loc_data.get(local_key)) != "" and _norm(location_obj.get(remote_key)) != _norm(loc_data.get(local_key)):
                            matches_optional = False
                            break

                    if matches_optional:
                        return location_obj.get('uri')

        print(f"WARNING: Could not find location: {loc_title}")
        return None
    except Exception as e:
        print(f"Error searching for location {loc_title}: {e}")
        return None
