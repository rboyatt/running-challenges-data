
# This script aims to create a cache of the data sources that running-challenges
# (both the website and the extension) might need to get from the parkrun website
# over and above the per-user information for the badges.

# Data:
# 5k parkrun event locations
# 2k parkrun event locations
# list of countries
# extra event info, including status (live, accepting registrations, etc...)

# Each of these pieces of data will be provided separately, and also in a
# single large file - which will be additionally be available as a compressed
# version to lessen the data bandwidth.

import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
import urllib.request
import os
import argparse

URL_GEO_XML_5K = 'https://www.parkrun.org.uk/wp-content/themes/parkrun/xml/geo.xml'
URL_GEO_XML_2K = 'https://www.parkrun.org.uk/wp-content/themes/parkrun/xml/geojuniors.xml'
URL_WIKI_TECHNICAL_EVENT_INFO = 'https://wiki.parkrun.com/index.php/Technical_Event_Information'

def fetch_webpage(url, retries=3, minimum_retry_wait_secs=30):

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    data = None

    download_page = None

    retry_attempt = 0

    while download_page is None and retry_attempt < retries:

        try:

            req = urllib.request.Request(url, data, headers)
            with urllib.request.urlopen(req) as response:
               download_page = response.read()

        except urllib.error.URLError as e:
            print(e.reason)
            sleep(minimum_retry_wait_secs)
        finally:
            retry_attempt += 1

    return download_page

def parse_events(root):
    # Example event:
    # <e n="winchester" m="Winchester" c="97" id="280" r="17" la="51.069286" lo="-1.310849"/>

    events = root.findall('e')
    print(len(events))

    parsed_events = dict()
    errored_events = list()

    for e in events:

        parsed_event = {
            'n': None,
            'm': None,
            'c': None,
            'id': None,
            'r': None,
            'la': None,
            'lo': None
        }

        mappings = {
            'n': ('n',),
            'm': ('m',),
            'c': ('c',),
            'id': ('id',),
            'r': ('r',),
            'la': ('la', 'float'),
            'lo': ('lo', 'float')
        }

        any_errors = False

        for key, props in mappings.items():
            try:
                value = e.get(key, None)
                if value is not None:
                    if len(props) > 1:
                        if props[1] == 'float':
                            value = float(value)
                    parsed_event[props[0]] = value
            except Exception as ex:
                any_errors = True
                print(ex)

        print(parsed_event)

        if any_errors:
            errored_events.append(parsed_event)
        else:
            parsed_events[parsed_event['n']] = parsed_event

    print('{} parsed events'.format(len(parsed_events)))
    print('{} errored events'.format(len(errored_events)))
    for ee in errored_events:
        print(ee)

    return parsed_events

def find_regions_recursively(node, result):
    for item in node.findall('r'):
        result.append(item)
        find_regions_recursively(item, result)
    return result

def parse_regions(region_list):

    countries = list()

    parsed_regions = list()
    errored_regions = list()

    # Example region:
    # <r id="2" n="UK" la="54.597527" lo="-2.460938" z="5" pid="1" u="http://www.parkrun.org.uk">

    for r in region_list:

        parsed_region = {
            'n': None,
            'id': None,
            'pid': None,
            'u': None,
            'la': None,
            'lo': None
        }

        mappings = {
            'n': ('n',),
            'pid': ('pid',),
            'id': ('id',),
            'u': ('u',),
            'la': ('la', 'float'),
            'lo': ('lo', 'float')
        }

        any_errors = False

        for key, props in mappings.items():
            try:
                value = r.get(key, None)
                if value is not None:
                    if len(props) > 1:
                        if props[1] == 'float':
                            value = float(value)
                    parsed_region[props[0]] = value
            except Exception as ex:
                any_errors = True
                print(ex)

        print(parsed_region)

        if any_errors:
            errored_regions.append(parsed_region)
        else:
            parsed_regions.append(parsed_region)
            if parsed_region.get('pid', None) == '1':
                countries.append(parsed_region)

    print('{} parsed regions'.format(len(parsed_regions)))
    print('{} errored regions'.format(len(errored_regions)))
    for ee in errored_regions:
        print(ee)

    print('{} countries'.format(len(countries)))
    print(countries)

    return (parsed_regions, countries)

def fetch_and_parse_geo_xml(url):

    geo_xml_file = fetch_webpage(url)
    print('geo_xml file length: {}'.format(len(geo_xml_file)))

    root = ET.fromstring(geo_xml_file)
    # root = tree.getroot()

    parsed_5k_events = parse_events(root)

    all_regions = list()
    find_regions_recursively(root, all_regions)
    (parsed_regions, countries) = parse_regions(all_regions)

    return (parsed_5k_events, parsed_regions, countries)

def fetch_and_parse_technical_event_information():

    parsed_tei_data = dict()

    tei_data = fetch_webpage(URL_WIKI_TECHNICAL_EVENT_INFO)
    print('tei_data file length: {}'.format(len(tei_data)))

    soup = BeautifulSoup(tei_data, 'html.parser')

    # Normally, the wiki will return a page with the following div:

    # 								<!-- bodycontent -->
    # 				<div id="mw-content-text" lang="en" dir="ltr" class="mw-content-ltr"><table class="wikitable sortable">
    # <tr>
    # <th>Event</th>
    # <th>Event Director</th>
    # <th>Event Number</th>
    # <th>Status</th>
    # <th>Country</th>
    # <th>Portal Number
    # </th></tr>
    # <tr>
    # <td><a href="/index.php/Aberbeeg_parkrun" title="Aberbeeg parkrun">Aberbeeg parkrun</a>
    # </td>
    # <td>Hayley Edwards
    # </td>
    # <td>2159
    # </td>
    # <td>Live
    # </td>
    # <td>United Kingdom
    # </td>
    # <td>2563
    # </td></tr>
    # <tr>
    # <td><a href="/index.php/Aberdare_parkrun" title="Aberdare parkrun">Aberdare parkrun</a>
    # </td>
    # <td>Adrian Harford

    # Attempt to find all of the divs with this id, just in case there is more
    # than one, or maybe zero
    # Find the first div with this tag, and then the first table within it

    page_container = soup.find(id="mw-content-text")
    if page_container is not None:
        possible_content_tables = page_container.find_all('table')

        print('Found {} table elements'.format(len(possible_content_tables)))

        for content_table in possible_content_tables:
            table_event_info = dict()
            # Find the first tr element, and check that it looks like a header row,
            # with headers we like the look of, as a sanity check
            print('Found potential table element')
            table_rows = content_table.find_all('tr')
            if len(table_rows) > 0:
                # Sanity check the first row
                header_row = table_rows[0]
                # Does it contain <th> elements?
                table_header_row_elements = content_table.find_all('th')
                print('{} th elements'.format(len(table_header_row_elements)))
                # Break out of processing this div if there are no th elements
                if len(table_header_row_elements) == 0:
                    continue
                column_headers = [th.get_text().strip() for th in table_header_row_elements]
                print(column_headers)
                column_header_mapping = {
                    'Event': 'e',
                    'Event Director': 'ed',
                    'Event Number': 'en',
                    'Status': 'es',
                    'Country': 'ec',
                    'Portal Number': 'ep'
                }

                if column_headers[0] != 'Event':
                    print('No Event column found')
                    continue

                # Iterate over all of the other rows
                print('Processing {} event information rows'.format(len(table_rows[1:])))
                for table_content_row in table_rows[1:]:
                    table_content_row_elements = table_content_row.find_all('td')

                    this_event_info = dict()

                    # Iterate over each column name
                    for idx,column_header in enumerate(column_headers):
                        # Just in case there are fewer columns in the body of the table,
                        # guard against refering ones that don't match the headers
                        if idx < len(table_content_row_elements):
                            # See if it is a column we want to make a note of,
                            # find the field name from the mapping dictionary, and
                            # add it to the info for this event
                            if column_header in column_header_mapping:
                                this_event_info[column_header_mapping[column_header]] = table_content_row_elements[idx].get_text().strip()

                    print(this_event_info)
                    # Add this event to the collection, as long as the event number is available
                    if 'en' in this_event_info:
                        table_event_info[this_event_info['en']] = this_event_info

            # Save the data if it looks like we have found some valid info
            if len(table_event_info) > 0:
                parsed_tei_data = table_event_info

    return parsed_tei_data

def write_json_file(filename, data):
    # Comparisons of pretty printed whitespace, versus none, all with longer field names:
    # -rw-r--r--  1 ataylor  staff    63K  6 Jan 18:52 parkrun-2k-events.json
    # -rw-r--r--  1 ataylor  staff    53K  6 Jan 18:52 parkrun-2k-events.min.json
    # -rw-r--r--  1 ataylor  staff   288K  6 Jan 18:52 parkrun-5k-events.json
    # -rw-r--r--  1 ataylor  staff   240K  6 Jan 18:52 parkrun-5k-events.min.json
    # -rw-r--r--  1 ataylor  staff   3.1K  6 Jan 18:52 parkrun-countries.json
    # -rw-r--r--  1 ataylor  staff   2.5K  6 Jan 18:52 parkrun-countries.min.json
    # -rw-r--r--  1 ataylor  staff    12K  6 Jan 18:52 parkrun-regions.json
    # -rw-r--r--  1 ataylor  staff    10K  6 Jan 18:52 parkrun-regions.min.json

    # Compared with using the bare minimum for the field names, as per the XML format:
    # -rw-r--r--  1 ataylor  staff    50K  6 Jan 18:58 parkrun-2k-events.json
    # -rw-r--r--  1 ataylor  staff    40K  6 Jan 18:58 parkrun-2k-events.min.json
    # -rw-r--r--  1 ataylor  staff   221K  6 Jan 18:58 parkrun-5k-events.json
    # -rw-r--r--  1 ataylor  staff   173K  6 Jan 18:58 parkrun-5k-events.min.json
    # -rw-r--r--  1 ataylor  staff   2.6K  6 Jan 18:58 parkrun-countries.json
    # -rw-r--r--  1 ataylor  staff   2.0K  6 Jan 18:58 parkrun-countries.min.json
    # -rw-r--r--  1 ataylor  staff    11K  6 Jan 18:58 parkrun-regions.json
    # -rw-r--r--  1 ataylor  staff   8.3K  6 Jan 18:58 parkrun-regions.min.json

    # By sorting the keys the diff in git should be reasonable, and we will be
    # able to spot the changes

    # Indenting the output makes it easier to read, but larger to transfer, although
    # compression will probably do a good job at making it smaller.

    # Using gzip on the largest files, the 5k events, we get the size down from
    # 221K/183K to 48K/46K. So it is still worh removing the whitespace, but it
    # is not that much of a penalty.

    # It will be useful to see if the Github pages hosting automatically passes
    # it as a compressed gzip file, or not, I believe it may if requested in the
    # right way.

    with open('{}.json'.format(os.path.join('.', filename)), 'w') as FH:
        json.dump(data, FH, sort_keys=True, indent=2)
    with open('{}.min.json'.format(os.path.join('.', filename)), 'w') as FH:
        json.dump(data, FH, sort_keys=True)

def update_parkrun_event_info_by_id(events, parkrun_event_info, properties=None):

    for event_name, event_info in events.items():
        # Check if this event has a matching property set
        event_id = event_info.get('id', None)
        if event_id is not None and event_id in parkrun_event_info:
            # Add all the properties if we haven't been supplied a subset
            if properties is None:
                event_info.update(parkrun_event_info[event_id])
            else:
                # Add each property explicitly requested, if available
                for prop in properties:
                    if prop in parkrun_event_info[event_id]:
                        event_info[prop] = parkrun_event_info[event_id][prop]

# Fetch and parse the data

print('Fetching parkrun data sources')

# N.B. The region data is idential for the two sets of parkrun event types, and
# includes all countries, even if they don't have any parkruns anymore, or in the case
# of juniors, don't have any parkruns yet :)
# - This means that we only need to parse one of these.
(parsed_5k_events, parsed_5k_regions, parsed_5k_countries) = fetch_and_parse_geo_xml(URL_GEO_XML_5K)
(parsed_2k_events, parsed_2k_regions, parsed_2k_countries) = fetch_and_parse_geo_xml(URL_GEO_XML_2K)

parkrun_event_info = fetch_and_parse_technical_event_information()

print('Fetched parkrun data sources')

# Write a copy of each of the files to disk for reference
reference_files = [
    ('parkrun-5k-events', parsed_5k_events),
    ('parkrun-2k-events', parsed_2k_events),
    ('parkrun-regions', parsed_5k_regions),
    ('parkrun-countries', parsed_5k_countries),
    ('parkrun-event-info', parkrun_event_info)
]
# print(reference_files)
for ref_file in reference_files:
    print(ref_file[0])
    write_json_file(*ref_file)

# Merge the data sources together by adding the event status to each of the
# parkrun events
for events in [parsed_5k_events, parsed_2k_events]:
    update_parkrun_event_info_by_id(events, parkrun_event_info, ['es'])

geo_data = {
    'countries' : parsed_5k_countries,
    'regions': parsed_5k_regions,
    'events_5k': parsed_5k_events,
    'events_2k': parsed_2k_events
}

print('Writing out master geo-data file')
write_json_file('geo', geo_data)

exit()
