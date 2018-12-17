#!/bin/bash

YEAR=${1:-"2018-19"}

echo "Fetching files for ${YEAR}"

# All the special events pages, as listed at
# https://www.parkrun.com/christmas-and-new-year/
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.com.au/special-events/ >  "${YEAR}/raw/au.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ca/special-events/ >  "${YEAR}/raw/ca.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.dk/special-events/ >  "${YEAR}/raw/dk.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.fi/special-events/ >  "${YEAR}/raw/fi.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.fr/special-events/ >  "${YEAR}/raw/fr.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.com.de/special-events/ >  "${YEAR}/raw/de.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ie/special-events/ >  "${YEAR}/raw/ie.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.it/special-events/ >  "${YEAR}/raw/it.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.my/special-events/ >  "${YEAR}/raw/my.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.co.nz/special-events/ >  "${YEAR}/raw/nz.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.no/special-events/ >  "${YEAR}/raw/no.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.pl/special-events/ >  "${YEAR}/raw/pl.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ru/special-events/ >  "${YEAR}/raw/ru.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.sg/special-events/ >  "${YEAR}/raw/sg.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.co.za/special-events/ >  "${YEAR}/raw/za.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.se/special-events/ >  "${YEAR}/raw/se.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.org.uk/special-events/ >  "${YEAR}/raw/uk.html"
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.us/special-events/ >  "${YEAR}/raw/us.html"
