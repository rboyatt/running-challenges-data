
import xml.etree.ElementTree as ET
import json
import os

from bs4 import BeautifulSoup

def parse_special_events_table(table, country_code, special_events_data, year):

    special_events = dict()

    # Find all of the table rows in the provided table
    table_rows = table.find_all('tr')
    print('{} table rows found'.format(len(table_rows)))

    if table_rows:
        column_map = dict()
        event_types = dict()
        # Pop the header row off, and assign the rest to the contents
        header_row = table_rows[0]
        content_rows = table_rows[1:]

        for index, th in enumerate(header_row.find_all('th')):
            column_heading = th.get_text().strip()

            # Find which event this in, taking into account the language barriers
            # If it is a top level event name, then it is in English and it is fine
            # to carry on with that, else we iterate through the regional variations
            # and find which the English equivalent is
            if column_heading not in special_events_data['translations']:
                for column, column_translations in special_events_data['translations'].items():
                    # Do a comparison in the lower case versions
                    if column_heading.lower() in [c.lower() for c in column_translations] + [column.lower()]:
                        print('Mapping {} to {}'.format(column_heading, column))
                        column_heading = column

            column_map[column_heading] = index
            # The first two colums contain the event, the later columns contain
            # the events which vary between countries
            if index >= 2:
                event_types[column_heading] = {
                    'index': index,
                    'date': special_events_data.get(column_heading, dict()).get('dates', dict()).get(year),
                    'events': dict()
                }

        # print(column_map)
        print(event_types)

        print('{} content rows found'.format(len(content_rows)))
        for r in content_rows:
            event_info = {
                'longname': None,
                'shortname': None,
                'country_domain': None,
                'country_code': country_code
            }
            cells = r.find_all('td')
            event_info['longname'] = cells[column_map['Event']].get_text().strip()
            event_url = cells[column_map['Event']].find('a')
            if event_url is not None:
                event_full_http_url = event_url['href']
                parts = event_full_http_url.split('/')
                event_info['country_domain'] = parts[2]
                event_info['shortname'] = parts[3]

            for special_event_type in event_types.keys():
                event_time = cells[column_map[special_event_type]].get_text().strip()
                # Create a new object for this event
                event_time_info = {
                    'time': event_time
                }
                # Merge in the rest of the details
                event_time_info.update(event_info)
                if len(event_time) > 2 and ',' not in event_time :
                    # print('{} @ {}'.format(special_event_type, event_time))
                    event_types[special_event_type]['events'][event_info['longname']] = event_time_info

        # print(event_types)
        # for event_type in event_types:
        #     print('{} x{}'.format(event_type, len(event_types[event_type]['events'])))

    return event_types


special_events_data = {
    'Thanksgiving': {
        'dates': {
            '2018-19': '2018-11-22',
            '2019-20': '2018-11-28'
        }
    },
    'Christmas Eve': {
        'dates': {
            '2018-19': '2018-12-24',
            '2019-20': '2019-12-24'
        }
    },
    'Christmas Day': {
        'dates': {
            '2018-19': '2018-12-25',
            '2019-20': '2019-12-25'
        }
    },
    'Boxing Day': {
        'dates': {
            '2018-19': '2018-12-26',
            '2019-20': '2019-12-26'
        }
    },
    'New Year\'s Day': {
        'dates': {
            '2018-19': '2019-01-01',
            '2019-20': '2020-01-01'
        }
    },
    'Orthodox Christmas': {
        'dates': {
            '2018-19': '2019-01-07',
            '2019-20': '2020-01-07'
        }
    },
    'Chinese New Year': {
        'dates': {
            '2018-19': '2019-02-05',
            '2019-20': '2020-01-20'
        }
    },
    'translations': {
        'Event': [
            'Standorte',
            'Evento',
            'Lokalizacja',
            'Забег'
        ],
        'Region': [
            'Område',
            'Regione',
            'Регион'
        ],
        'Thanksgiving': [
        ],
        'Christmas Eve': [
            'Juledag'
        ],
        'Christmas Day': [
            'Noël',
            'Natale'
        ],
        'Boxing Day': [
            '2. Weihnachtsfeiertag',
            'Drugi Dzień Świąt',
        ],
        'New Year\'s Day': [
            'Nytårsdag',
            'Jour de l\'an',
            'Neujahr',
            'Capodanno',
            'Nowy Rok',
            'Новый год',
        ],
        'Orthodox Christmas': [
            'Рождество'
        ],
        'Chinese New Year': [
        ]

    }
}

# Make this a parameter at some point, but for now, it's hardcoded
this_year = '2019-20'

input_files = dict()
# Load the entire page, in all its messy glory

raw_data_directory = '../../data/parkrun-special-events/{}/raw/'.format(this_year)
for file in os.listdir(raw_data_directory):
    if file.endswith('.html'):
        # String the ending off
        country_code = os.path.splitext(file)[0]
        input_files[country_code] = os.path.join(raw_data_directory, file)

print(input_files)

all = dict()

for country_code, raw_file_path in input_files.items():

    print('Processing {} - {}'.format(country_code, raw_file_path))

    soup = None
    with open(raw_file_path, 'r') as FH:
        html_doc = FH.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

    # Find the 'results' table that contains the data for what parkruns are putting
    # on the special events
    main_table = soup.find_all(id="results")
    print('{} matching tables found'.format(len(main_table)))

    # Assume it is the only table
    if len(main_table) >= 1:
        special_events = parse_special_events_table(main_table[0], country_code, special_events_data, this_year)

        # Merge this country's special events into the master list
        for event_type, event_details in special_events.items():
            # If this event, e.g. Christmas Day is not known about yet, then
            # pre-populate it with this country's info
            if event_type not in all:
                all[event_type] = event_details
            # Else, append the lists of parkrun events from this country to the
            # existing list
            else:
                all[event_type]['events'].update(event_details['events'])

        with open('../../data/parkrun-special-events/{}/parsed/{}.json'.format(this_year, country_code), 'w') as FH:
            json.dump(special_events, FH, sort_keys=True, indent=2)
    # print(json.dumps(geo_data, sort_keys=True, indent=2))

# Worldwide summary:
for event_type, event_details in all.items():
    print('{} - {} events'.format(event_type, len(event_details['events'])))

with open('../../data/parkrun-special-events/{}/parsed/all.json'.format(this_year), 'w') as FH:
    json.dump(all, FH, sort_keys=True, indent=2)

# print(soup.prettify())

exit(0)
