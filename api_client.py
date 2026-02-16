import requests

import re
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple

import os

# Constants
BASE_URL = "https://apps.daysmartrecreation.com/dash/jsonapi/api/v1"
COMPANY_SLUG = os.getenv("COMPANY_SLUG", "sharks")
FACILITY_ID = os.getenv("FACILITY_ID", "1")
SPORT_ID = os.getenv("SPORT_ID", "27")

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_events(target_date: date) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetches events for the specified date.
    """
    url = f"{BASE_URL}/events"
    
    start_date_str = target_date.strftime("%Y-%m-%d")
    end_date_str = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    params = {
        'cache[save]': 'false',
        'page[size]': '50',
        'sort': 'end,start',
        'include': 'summary,comments,resource.facility.address,resource.address,eventType.product.locations,homeTeam.facility.address,homeTeam.league.season.priorities.memberships,homeTeam.league.season.priorities.activatedBySeasons,homeTeam.programType,homeTeam.product,homeTeam.product.locations,homeTeam.sport',
        'filter[start_date__gte]': start_date_str,
        'filter[start_date__lte]': end_date_str,
        'filter[unconstrained]': '1',
        'filter[homeTeam.sport_id__in]': SPORT_ID,
        'filterRelations[comments.comment_type]': 'public',
        'company': COMPANY_SLUG
    }
    
    headers = {
        'Accept': 'application/vnd.api+json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    print(f"Fetching events from: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []), data.get('included', [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return [], []

def check_availability(events: List[Dict], included: List[Dict]) -> List[Dict]:
    """
    Parses events and returns a list of available sessions.
    """
    available_sessions = []
    
    included_map = {}
    for item in included:
        key = (item['type'], item['id'])
        included_map[key] = item['attributes']

    for event in events:
        event_id = event['id']
        attrs = event['attributes']
        
        # Name extraction
        name = attrs.get('name')
        if not name:
            desc = attrs.get('best_description')
            if desc:
                name = clean_html(desc)
            else:
                name = "Unnamed Session"
        
        start_time = attrs.get('start')
        
        # Availability Logic
        is_available = False
        openings = 0
        status = "unknown"
        
        if 'summary' in event.get('relationships', {}):
             summary_ref = event['relationships']['summary']['data']
             if summary_ref:
                 summary_attrs = included_map.get((summary_ref['type'], summary_ref['id']))
                 if summary_attrs:
                     open_slots = summary_attrs.get('open_slots', 0)
                     rem_reg_slots = summary_attrs.get('remaining_registration_slots', 0)
                     reg_status = summary_attrs.get('registration_status')
                     
                     if (open_slots > 0 or rem_reg_slots > 0) and reg_status != 'closed':
                         is_available = True
                         openings = max(open_slots, rem_reg_slots)

                         # Facility Check
                         if 'resource' in event.get('relationships', {}):
                             res_ref = event['relationships']['resource']['data']
                             if res_ref:
                                 res_attrs = included_map.get((res_ref['type'], res_ref['id']))
                                 if res_attrs:
                                     res_facility_id = str(res_attrs.get('facility_id'))
                                     if res_facility_id != FACILITY_ID: 
                                         is_available = False
                         
                     # Improve name from summary if available
                     if summary_attrs.get('name'):
                         name = summary_attrs.get('name')

                     status = f"{reg_status} (Slots: {open_slots}, RemReg: {rem_reg_slots})"

        print(f"Event: {name} | Start: {start_time} | Status: {status} | Available: {is_available}")
        
        if is_available:
            # Extract YYYY-MM-DD from start_time (which is ISO format)
            date_str = start_time.split('T')[0]
            available_sessions.append({
                'name': name,
                'start': start_time,
                'openings': openings,
                'link': f"https://apps.daysmartrecreation.com/dash/x/#/online/{COMPANY_SLUG}/event-registration?facility_ids={FACILITY_ID}&event_id={event_id}&date={date_str}"
            })
            
    return available_sessions
