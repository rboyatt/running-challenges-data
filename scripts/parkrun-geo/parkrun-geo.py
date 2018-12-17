
import xml.etree.ElementTree as ET
import json

def parse_events(root):
    # Example event:
    # <e n="winchester" m="Winchester" c="97" id="280" r="17" la="51.069286" lo="-1.310849"/>

    events = root.findall('e')
    print(len(events))

    parsed_events = dict()
    errored_events = list()

    for e in events:

        parsed_event = {
            'name': None,
            'local_name': None,
            'country_id': None,
            'event_id': None,
            'region_id': None,
            'latitude': None,
            'longitude': None
        }

        mappings = {
            'n': ('name',),
            'm': ('local_name',),
            'c': ('country_id',),
            'id': ('event_id',),
            'r': ('region_id',),
            'la': ('latitude', 'float'),
            'lo': ('longitude', 'float')
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
            parsed_events[parsed_event['name']] = parsed_event

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
            'name': None,
            'id': None,
            'parent_id': None,
            'url': None,
            'latitude': None,
            'longitude': None
        }

        mappings = {
            'n': ('name',),
            'pid': ('parent_id',),
            'id': ('id',),
            'u': ('url',),
            'la': ('latitude', 'float'),
            'lo': ('longitude', 'float')
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
            if parsed_region.get('parent_id', None) == '1':
                countries.append(parsed_region)

    print('{} parsed regions'.format(len(parsed_regions)))
    print('{} errored regions'.format(len(errored_regions)))
    for ee in errored_regions:
        print(ee)

    print('{} countries'.format(len(countries)))
    print(countries)

    return (parsed_regions, countries)

geo_xml_file = '../../data/parkrun-geo/raw/geo.xml'
tree = ET.parse(geo_xml_file)
root = tree.getroot()

parsed_5k_events = parse_events(root)

all_regions = list()
find_regions_recursively(root, all_regions)
(parsed_regions, countries) = parse_regions(all_regions)

geo_juniors_xml_file = '../../data/parkrun-geo/raw/geo-juniors.xml'
tree = ET.parse(geo_juniors_xml_file)
parsed_2k_events = parse_events(tree.getroot())

geo_data = {
    'countries' : countries,
    'regions': parsed_regions,
    'events_5k': parsed_5k_events,
    'events_2k': parsed_2k_events
}

with open('../../data/parkrun-geo/parsed/geo.json', 'w') as FH:
    json.dump(geo_data, FH, sort_keys=True, indent=2)

print(json.dumps(geo_data, sort_keys=True, indent=2))
