"""
ArchivesSpace JSON templates for creating new objects.
These templates are used when creating new records via the API.
"""

def archival_object():
    """Template for a new archival object"""
    return {
        "jsonmodel_type": "archival_object",
        "external_ids": [],
        "subjects": [],
        "linked_events": [],
        "extents": [],
        "dates": [],
        "external_documents": [],
        "rights_statements": [],
        "linked_agents": [],
        "restrictions_apply": False,
        "instances": [],
        "notes": [],
        "title": "",
        "level": ""
    }

def top_container(type=None, indicator=None):
    """Template for a new top container"""
    container = {
        "jsonmodel_type": "top_container",
        "container_locations": [],
        "restricted": False,
        "active_restrictions": []
    }
    if type is not None:
        container["type"] = str(type)
    if indicator is not None:
        container["indicator"] = str(indicator)
    return container

def digital_object(title, file_url, digital_object_id=None):
    """Template for a new digital object"""
    import uuid
    if digital_object_id is None:
        digital_object_id = str(uuid.uuid4())
    
    return {
        "jsonmodel_type": "digital_object",
        "external_ids": [],
        "subjects": [],
        "linked_events": [],
        "extents": [],
        "dates": [],
        "external_documents": [],
        "rights_statements": [],
        "linked_agents": [],
        "file_versions": [{
            "jsonmodel_type": "file_version",
            "publish": True,
            "is_representative": True,
            "file_uri": file_url,
            "use_statement": "",
            "xlink_actuate_attribute": "none",
            "xlink_show_attribute": "embed"
        }],
        "restrictions": False,
        "notes": [],
        "linked_instances": [],
        "title": title,
        "language": "",
        "digital_object_id": digital_object_id
    }

def date_object(date_begin, date_end=None, display_date=None, date_type=None):
    """Template for a date object"""
    if date_end and len(str(date_end)) > 0:
        date_type = date_type or "inclusive"
        date = {
            "jsonmodel_type": "date",
            "date_type": date_type,
            "label": "creation",
            "begin": str(date_begin),
            "end": str(date_end)
        }
    else:
        date_type = date_type or "single"
        date = {
            "jsonmodel_type": "date",
            "date_type": date_type,
            "label": "creation",
            "begin": str(date_begin)
        }
    
    if display_date:
        date["expression"] = str(display_date)
    
    return date

def note_multipart(note_type, text, label=None):
    """Template for a multipart note"""
    note = {
        "type": note_type,
        "jsonmodel_type": "note_multipart",
        "publish": True,
        "subnotes": [{
            "content": text,
            "jsonmodel_type": "note_text",
            "publish": True
        }]
    }
    if label:
        note["label"] = label
    return note

def instance_with_container(container_uri, type2=None, indicator2=None):
    """Template for an instance with a top container"""
    instance = {
        "jsonmodel_type": "instance",
        "instance_type": "mixed_materials",
        "is_representative": True,
        "sub_container": {
            "jsonmodel_type": "sub_container",
            "top_container": {
                "ref": container_uri
            }
        }
    }
    if type2:
        instance["sub_container"]["type_2"] = type2
    if indicator2:
        instance["sub_container"]["indicator_2"] = indicator2
    return instance

def instance_with_digital_object(dao_uri, is_representative=True):
    """Template for an instance with a digital object"""
    return {
        "jsonmodel_type": "instance",
        "digital_object": {
            "ref": dao_uri
        },
        "instance_type": "digital_object",
        "is_representative": is_representative
    }

def container_location(location_uri, status="current", note=None, start_date=None, end_date=None):
    """Template for a container location"""
    from datetime import datetime
    if start_date is None:
        start_date = datetime.now().isoformat().split("T")[0]
    
    location = {
        "status": status,
        "jsonmodel_type": "container_location",
        "start_date": start_date,
        "ref": location_uri
    }
    if note:
        location["note"] = note
    if end_date:
        location["end_date"] = end_date
    return location
