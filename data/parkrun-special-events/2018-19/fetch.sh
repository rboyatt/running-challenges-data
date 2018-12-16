# Standard English column headings
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.org.uk/special-events/ > raw/uk.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.com.au/special-events/ > raw/au.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ie/special-events/ > raw/ie.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.co.za/special-events/ > raw/za.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.co.nz/special-events/ > raw/nz.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.us/special-events/ > raw/us.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ca/special-events/ > raw/ca.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.se/special-events/ > raw/se.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.no/special-events/ > raw/no.html
curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.fi/special-events/ > raw/fi.html

# These are not in English, so don't work just yet
# curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.ru/special-events/ > raw/ru.html
# curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.pl/special-events/ > raw/pl.html
# curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.dk/special-events/ > raw/dk.html
# curl -H 'user-agent: Mozilla/Firefox' https://www.parkrun.fr/special-events/ > raw/fr.html
