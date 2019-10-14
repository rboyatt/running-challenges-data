#!/usr/bin/python

import json
from geopy.distance import vincenty

this_year='2019-20'
SEARCHDISTANCE = 40

parsed_data_directory = '../../data/parkrun-special-events/{}/parsed/'.format(this_year)
geofile = "../../data/parkrun-geo/parsed/geo.json"

events = []


def find_events_near(lat, long):
    nearbyevents = []

    elatlong = (lat, long)

    for key, e in events.items():
        olatlong = (e['latitude'], e['longitude'])
        distance = vincenty(elatlong, olatlong).km

        if distance <= SEARCHDISTANCE:
            nearbyevents.append(e)

    return nearbyevents

# Load event data, as we need the geo information
with open(geofile, 'r') as GFH:
    geodata = json.load(GFH)

    events5k = 'events_5k'
    if events5k in geodata.keys():
        events = geodata[events5k]

# Load the special events data
with open(parsed_data_directory + '/all.json', 'r') as FH:

    # Extract JSON data from this file
    data = json.load(FH)

    nyd = "New Year\'s Day"
    if nyd in data.keys():

        runningonnyd = []
        for a, b in data[nyd]['events'].items():
            runningonnyd.append(b['shortname'])

        # Examine events
        for key, event in data[nyd]['events'].items():

            print("Examing event: " + key + " known as " + event['longname'])

            # Where is this event?
            if event['shortname'] in events:
                lat = events[event['shortname']]['latitude']
                long = events[event['shortname']]['longitude']
            else:
                print("Cannot find " + event['shortname'] + ": " +event['longname'])

            if lat is not None and long is not None:
                # For each event, find those nearby also running an event
                nearbyevents = find_events_near(lat, long)

                print("Nearby events: " + str(len(nearbyevents)))

                # Filter for those which:
                # (a) have an event on NYD,
                # (b) are after the first event and
                # (c) also viable to reach

                runnearby = []
                for n in nearbyevents:
                    # Is this event actually running on NYD?
                    if n['name'] in runningonnyd:
                        runnearby.append(n)

                print("Running events: " + str(len(runnearby)))
                print(runnearby)
