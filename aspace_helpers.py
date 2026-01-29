"""
Helper functions for ArchivesSpace operations using archivessnake.
Provides convenience wrappers around common API operations.
"""
import json
from . import aspace_templates


def get_children_waypoint(client, resource_uri, node_uri=None):
    """Get children of a resource or archival object using waypoint API"""
    children = []
    try:
        if node_uri is None:
            tree = client.get(resource_uri + '/tree/root').json()
        else:
            tree = client.get(resource_uri + '/tree/node', params={'node_uri': node_uri}).json()
        
        max_offset = tree.get('waypoints', 0)
        
        for i in range(max_offset):
            batch_params = {'offset': i}
            if node_uri is not None:
                batch_params['parent_node'] = node_uri
            batch = client.get(resource_uri + '/tree/waypoint', params=batch_params).json()
            for child in batch:
                children.append({'record_uri': child['uri'], 'title': child.get('title', '')})
    except Exception as e:
        print(f"Error getting children: {e}")
    return children


def get_resource_by_id(client, repository, identifier):
    """Get a resource by its identifier (id_0)"""
    aq = json.dumps({"query": {"field": "identifier", "value": identifier, "jsonmodel_type": "field_query"}})
    search_results = client.get(f'repositories/{repository}/search', params={'page': '1', 'aq': aq}).json()
    
    if search_results.get('total_hits', 0) > 0:
        resource_uri = search_results['results'][0]['uri']
        return client.get(resource_uri).json()
    return None


def get_archival_object_by_ref_id(client, repository, ref_id):
    """Get an archival object by its ref_id"""
    ao_result = client.get(f'repositories/{repository}/find_by_id/archival_objects', params={'ref_id[]': ref_id}).json()
    
    if ao_result.get('archival_objects'):
        ao_uri = ao_result['archival_objects'][0]['ref']
        return client.get(ao_uri).json()
    return None


def post_archival_object(client, repository, ao_object):
    """Post an archival object (create or update)"""
    if "ref_id" in ao_object and "uri" in ao_object:
        # Update existing
        return client.post(ao_object['uri'], json=ao_object)
    else:
        # Create new
        return client.post(f'/repositories/{repository}/archival_objects', json=ao_object)


def post_container(client, repository, container_object):
    """Post a top container (create or update)"""
    if "uri" in container_object:
        # Update existing
        return client.post(container_object['uri'], json=container_object)
    else:
        # Create new
        return client.post(f'/repositories/{repository}/top_containers', json=container_object)


def post_digital_object(client, repository, dao_object):
    """Post a digital object"""
    if "uri" in dao_object:
        return client.post(dao_object['uri'], json=dao_object)
    else:
        return client.post(f'/repositories/{repository}/digital_objects', json=dao_object)


def add_date_to_object(obj, date_begin, date_end=None, display_date=None):
    """Add a date to an object"""
    date = aspace_templates.date_object(date_begin, date_end, display_date)
    if 'dates' not in obj:
        obj['dates'] = []
    obj['dates'].append(date)
    return obj


def add_note_to_object(obj, note_type, text, label=None):
    """Add a multipart note to an object"""
    note = aspace_templates.note_multipart(note_type, text, label)
    if 'notes' not in obj:
        obj['notes'] = []
    obj['notes'].append(note)
    return obj


def add_container_to_object(obj, container_uri, type2=None, indicator2=None):
    """Add a container instance to an object"""
    instance = aspace_templates.instance_with_container(container_uri, type2, indicator2)
    if 'instances' not in obj:
        obj['instances'] = []
    obj['instances'].append(instance)
    return obj


def add_digital_object_to_object(obj, dao_uri, is_representative=True):
    """Add a digital object instance to an archival object"""
    instance = aspace_templates.instance_with_digital_object(dao_uri, is_representative)
    if 'instances' not in obj:
        obj['instances'] = []
    obj['instances'].append(instance)
    return obj


def add_location_to_container(container_obj, location_uri, note=None, status="current", start_date=None, end_date=None):
    """Add a location to a container"""
    location = aspace_templates.container_location(location_uri, status, note, start_date, end_date)
    if 'container_locations' not in container_obj:
        container_obj['container_locations'] = []
    container_obj['container_locations'].append(location)
    return container_obj


def remove_notes_by_type(obj, note_type):
    """Remove all notes of a specific type from an object"""
    if 'notes' in obj:
        obj['notes'] = [note for note in obj['notes'] if note.get('type') != note_type]
    return obj


def remove_container_instances(obj):
    """Remove all container instances from an object, keeping digital object instances"""
    if 'instances' in obj:
        obj['instances'] = [inst for inst in obj['instances'] if 'digital_object' in inst]
    return obj


def iso2DACS(normalDate):
    """Convert ISO date format to DACS display format"""
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
