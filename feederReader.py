#==================================================================
#
# feederReader : Retrieves ADSB Flight data from tar1090 feed
#                    parsing the JSON, sorting and then displaying
#                    the results.
#
###################################################################
#
# Author: Andy Holmes (2E0IJC)
# Date:   20th November 2023
#
###################################################################

import json
import geopy.distance

from operator import itemgetter

import requests

#==============================================================================================================
# Set Latitude and Longitude: used to calculate distance
QTH_LAT                            = 'SET'
QTH_LON                            = 'SET'

#==============================================================================================================
# Exclude - list Id / Hex codes to exclude from Flights
EXCLUDE = [ ]                            # '43bf94', '43bf95', '43bf96' are ground stations that I want to exclude from my list of flights

#==============================================================================================================
# MACH_SPD value to convert ADSB Mach values to km/h
MACH_SPD = 1200                   # Original setting 1235 - higher than shown on tar1090

#==============================================================================================================
URL      = "http://radiopi/tar1090/"
#URL      = "https://localhost/tar1090"                 # Local tar1090 feed
DATA     =  URL + "data/aircraft.json"         #Flight Data served up from URL

#==============================================================================================================
SCRIPT = "FeederReader"      # Script Name
#==============================================================================================================
# Header Information
HEADER_INFO = "Welcome to " + SCRIPT + "\t The Real time flight data review tool\n\nAttempting to retreive data....."

#==============================================================================================================
# Footer Information
FOOTER_INFO = "\n\nThank you for using " + SCRIPT + "\n\nGoodbye\n\n"


#  Trailer Details
TRAILER_INFO = "The Online Amateur Radio Community ADSB website: https://adsb.oarc.uk/\tADBS Wiki https://wiki.oarc.uk/flight:adsb\n"

#==============================================================================================================
#OARC Flight Link
FLIGHT_LINK           = URL + "?icao="

#==============================================================================================================
# Limit the number of flights to display 
MAX_DISPLAY           = 15

#==============================================================================================================
# Formatting for printing Flight Information
DEFAULT_FORMAT        = 'Id: {i[0]}\tCall: {i[1]}\tSwk: {i[14]}\tAlt: {i[2]}ft\tSpd: {i[7]}km/h\tDist: {i[22]}km\tHd: {i[8]}\tCo-Ord: [{i[20]} / {i[21]}]\tCat: {i[16]}\tMLAT: {i[34]}\tMsg: {i[36]}\tSeen: {i[37]}\tRSSI: {i[38]}'
DEFAULT_FORMAT_LINKS  = '\t{FLIGHT_LINK}{i[0]}'

EXTENDED_FORMAT       = ''
EXTENDED_FORMAT_LINKS = ''

#==============================================================================================================
# Formatting for Stats Update
Stats1               = '\tTotal Aircraft: {fltStats[9]}\t\tHighest:  Id:  {fltStats[0]}\tCall:  {fltStats[1]}\tAltitude: {fltStats[2]}m'
Stats2               = '\tWith Positions: {fltStats[10]}\t\tFastest: Id:  {fltStats[3]}\tCall:  {fltStats[4]}\tSpeed:    {fltStats[5]}km/h'
Stats3               = '\tTotal Exluded:  {fltStats[11]}\t\tFurthest: Id: {fltStats[6]}\tCall:  {fltStats[7]}\tDistance: {fltStats[8]}km'
Stats4               = '\tTotal MLAT:     {fltStats[12]}'

StatsURLLink1        = '\t{FLIGHT_LINK}{fltStats[0]}'
StatsURLLink2        = '\t{FLIGHT_LINK}{fltStats[3]}'
StatsURLLink3        = '\t{FLIGHT_LINK}{fltStats[6]}'



#==============================================================================================================


#==============================================================================================================
QTH                                = (QTH_LAT, QTH_LON)
#==============================================================================================================
SUCCESS                            = 200           # Successful response code
#==============================================================================================================
# Sort Flights with Positions by:
HEX                = 0           # Hex Id Code
CALL               = 1           # Call Sign
ALT                = 2           # Altitude / Height
SPD                = 7           # Speed (Calculated)
SWK                = 14          # Squawk Code
CAT                = 16          # Aircraft Category / Type
DST                = 22          # Distance (Calculated)
MLT                = 34          # MLAT
MSG                = 36          # Messages
SEN                = 37          # Seen
RSI                = 38          # RSSI: Received Signal Strength Indicator


SORT               = [HEX, CALL, ALT, SPD, SWK, CAT, DST, MLT, MSG, SEN, RSI]

# Statistics we can display
DEFAULT           = "XXXX"
UNKNOWN           = "XX"

HIGH_ID           = DEFAULT
HIGH_CALL         = DEFAULT
HIGHEST           = DEFAULT
FAST_ID           = DEFAULT
FAST_CALL         = DEFAULT
FASTEST           = DEFAULT
FURT_ID           = DEFAULT
FURT_CALL         = DEFAULT
FURTHEST          = DEFAULT


NUM_AIRCRAFT      = 0
NUM_NO_POSITIONS  = 0
NUM_EXLUDED       = 0
NUM_MLAT          = 0

#==============================================================================================================
# Command constant Values
QUIT              = 'q'
FLIGHTS           = 'f'
EXCLUDED          = 'e'
REVERSE           = 'r'
STATS             = 's'
JSON              = 'j'
SORT_ID           = 'i'
SORT_CALL         = 'c'
SORT_ALT          = 'a'
SORT_VELOCITY     = 'v'
SORT_SQUAWK       = 'k'
SORT_DISTANCE     = 'd'
SORT_CATEGORY     = 't'
SORT_MLAT         = 'm'
SORT_RSSI         = '^'
GET_DATA          = 'g'
EXTD_DATA         = 'x'
INC_LINKS         = 'l'
LIST_CMDS         = '?'
HELP              = 'h'

COMMANDS = [QUIT, FLIGHTS, EXCLUDED, REVERSE, STATS, JSON, SORT_ID, SORT_CALL, SORT_ALT, SORT_VELOCITY, SORT_SQUAWK, SORT_DISTANCE, SORT_CATEGORY, SORT_MLAT, SORT_RSSI, EXTD_DATA, GET_DATA, INC_LINKS, LIST_CMDS, HELP]

#==============================================================================================================
#==============================================================================================================
# Available Commands

CMD_STR  = f'''{SCRIPT}: Commands:

\t{STATS}\tStats - List Flight Stastics\t\t\t{FLIGHTS}\tFlights - List flights with Positions
\t{EXCLUDED}\tExcluded - List Excluded Flights\t\t{JSON}\tJSON Format - List Flights in Raw / JSON format
\t{GET_DATA}\tGet / Refresh Data\t\t\t\t{INC_LINKS}\tLinks - include / exclude
\t{LIST_CMDS}\tList available Commands

\t{QUIT}\tQuit the Application\t\t\t\t{HELP}\tHelp

\tSorting: Flights can be sorted by:
\t\t{SORT_ID}\tId / Hex\t\t{SORT_DISTANCE}\tDistance\t\t{SORT_ALT}\tAltitude\t\t{SORT_VELOCITY}\tVelocity / Speed
\t\t{SORT_CALL}\tCall Sign\t\t{SORT_SQUAWK}\tSquawk Code\t\t{SORT_CATEGORY}\tCategory / Type\t\t{SORT_MLAT}\tMLAT\t\t{SORT_RSSI}\tRSSI\n'''

#==============================================================================================================
#==============================================================================================================
# Help Information
HELP_STR1  = f"""{SCRIPT}: Help:
This script takes real-time Aircraft ADSB output from tar10190/data/aircraft.json, parses it and displays it.
It can help in understanding more about the information transmitted in ADSB transmissions.

The aircraft.json data is read into two lists, formatted and the raw JSON data. As the data is parsed, the script
also captures stats: <s>

Cmd: s
Real Time Flight information:

	Total Aircraft: 57		Highest:  Id: 4010ee	Call:  XXXX	    Altitude: 48100m	http://radiopi/tar1090/?icao=4010ee
	With Positions: 42		Fastest:  Id: 4bb183	Call:  THY29M  	  Speed:    1012km/h	http://radiopi/tar1090/?icao=4bb183
	Total Exluded:  3		Furthest: Id: 44061b	Call:  XXXX	    Distance: 392.5km	http://radiopi/tar1090/?icao=44061b
	Total MLAT:     8

The URL link can be included / excluded using the <l> command:

Cmd: l
Links is : False
Cmd: s
Real Time Flight information:

	Total Aircraft: 57		Highest:  Id: 4010ee	Call:  XXXX	    Altitude: 48100m
	With Positions: 42		Fastest:  Id: 4bb183	Call:  THY29M  	Speed:    1012km/h
	Total Exluded:  3		Furthest: Id: 44061b	Call:  XXXX	    Distance: 392.5km
	Total MLAT:     8

Flights are displayed by using the <f> command:

Cmd: f
Aircraft with Positions: 57

Id: 407f6e	Call: ABV4FS  	Swk: 5155	Alt: 22975ft	Spd: 700km/h	Dist: 245.3km	Hd: 126	Co-Ord: [53.98 / -4.88]	Cat: XX	MLAT: N	RSSI: -24.6
Id: 406c72	Call: EZY780W 	Swk: 6306	Alt: 25275ft	Spd: 830km/h	Dist: 290.5km	Hd: 320	Co-Ord: [52.46 / -0.78]	Cat: A3	MLAT: N	RSSI: -20.4
Id: 4ca7b9	Call: RYR95YZ 	Swk: 0474	Alt: 3725ft	    Spd: 388km/h	Dist: 69.1km	Hd: 227	Co-Ord: [54.41 / -1.62]	Cat: A3	MLAT: N	RSSI: -4.4
Id: 4cad9f	Call: XXXX	    Swk: XXXX	Alt: 46900ft	Spd: 0km/h	    Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: A2	MLAT: N	RSSI: -27.6
Id: 4ca625	Call: XXXX	    Swk: 5166	Alt: 0ft	    Spd: 0km/h	    Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: XX	MLAT: N	RSSI: -29.4
Id: 4009da	Call: XXXX	    Swk: XXXX	Alt: 27000ft	Spd: 960km/h	Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: XX	MLAT: N	RSSI: -14.7
Id: 407ac1	Call: TOM30T  	Swk: 7662	Alt: 35875ft	Spd: 960km/h	Dist: 326.3km	Hd: 44	Co-Ord: [52.45 / -3.90]	Cat: A3	MLAT: N	RSSI: -26.8


Extended information can be displayed using the <x> command:

Cmd: x
Extended Format is: True
Cmd: f
Aircraft with Positions: 57

Id: 407f6e	Call: ABV4FS  	Swk: 5155	Alt: 22975ft	Spd: 700km/h	Dist: 245.3km	Hd: 126	Co-Ord: [53.98 / -4.88]	Cat: XX	MLAT: N	Msg: 92	Seen: 0.2	RSSI: -24.6
	Emergency: None	Mach: 0.584	Baro Rate: 23075	Geom Rate: 397.0	Track Rate: 0.03	Roll: 0.0	
Id: 406c72	Call: EZY780W 	Swk: 6306	Alt: 25275ft	Spd: 830km/h	Dist: 290.5km	Hd: 320	Co-Ord: [52.46 / -0.78]	Cat: A3	MLAT: N	Msg: 1660	Seen: 0.1	RSSI: -20.4
	Emergency: none	Mach: 0.692	Baro Rate: 25225	Geom Rate: 395.0	Track Rate: 0.06	Roll: 0.0	
Id: 4ca7b9	Call: RYR95YZ 	Swk: 0474	Alt: 3725ft	Spd: 388km/h	    Dist: 69.1km	Hd: 227	Co-Ord: [54.41 / -1.62]	Cat: A3	MLAT: N	Msg: 1406	Seen: 0.1	RSSI: -4.4
	Emergency: none	Mach: 0.324	Baro Rate: 3875	Geom Rate: 233.5	Track Rate: 0.0	Roll: -0.7	

The formatted flights can be sorted by: 
\t<i>\tId / Hex Code\t\t<d>\tDistance\t\t<v>\tVelocity / Speed
\t<c>\tCall Sign\t\t<k>Squawk Code\t\t<t>\tAircraft Type
\t<m>\tMLAT\t\t<^>\tRSSI - Signal Strength

The <r> command can be used to Reverse the sort order.

Cmd: r
Reverse is: True
Cmd: i
Flights Sorted by [Id]

Id: a57ad0	Call: GTI8298 	Swk: 2207	Alt: 37000ft	Spd: 988km/h	Dist: 178.1km	Hd: 131	Co-Ord: [53.60 / -0.32]	Cat: A5	MLAT: N	RSSI: -20.0
Id: 4d2387	Call: RYR99HM 	Swk: 7667	Alt: 29000ft	Spd: 796km/h	Dist: 242.4km	Hd: 101	Co-Ord: [53.06 / -3.13]	Cat: A3	MLAT: N	RSSI: -15.2
Id: 4d22c3	Call: RYR57KK 	Swk: 2264	Alt: 24075ft	Spd: 820km/h	Dist: 191.0km	Hd: 104	Co-Ord: [53.33 / -1.15]	Cat: A3	MLAT: N	RSSI: -14.4
Id: 4cc4c5	Call: ABD387  	Swk: 2217	Alt: 35000ft	Spd: 998km/h	Dist: 229.4km	Hd: 130	Co-Ord: [53.44 / -3.79]	Cat: A5	MLAT: N	RSSI: -16.4


Cmd: i
Flights Sorted by [Id]

Id: 3986e7	Call: AFR67KR 	Swk: 5611	Alt: 16200ft	Spd: 662km/h	Dist: 72.9km	Hd: 10	Co-Ord: [54.39 / -1.79]	Cat: A3	MLAT: N	RSSI: -5.0
Id: 39e682	Call: AFR1886 	Swk: 5612	Alt: 38000ft	Spd: 902km/h	Dist: 240.2km	Hd: 327	Co-Ord: [52.92 / -0.78]	Cat: A3	MLAT: N	RSSI: -20.3
Id: 3c70c9	Call: GEC8188 	Swk: 6240	Alt: 32000ft	Spd: 988km/h	Dist: 188.2km	Hd: 278	Co-Ord: [53.37 / -1.00]	Cat: A5	MLAT: N	RSSI: -14.6
Id: 400796	Call: LOG7J   	Swk: 7736	Alt: 36000ft	Spd: 888km/h	Dist: 107.6km	Hd: 12	Co-Ord: [55.78 / -2.62]	Cat: XX	MLAT: Y	RSSI: -13.8

The data can be refreshed using the <g< command and updates the stats, formatted and raw JSON data.

The raw JSON data can be viewed using the <j> command for a better understanding of the data.
"""
HELP_STR2 = """
Cmd: j
{"hex": "80153d", "alt_baro": 35000, "alt_geom": 35200, "gs": 532.9, "track": 124.9, "baro_rate": 0, "squawk": "2221", "lat": 55.785129, "lon": -4.924793, "nic": 8, "rc": 186, "seen_pos": 12.2, "version": 0, "nac_p": 8, "nac_v": 1, "sil": 2, "sil_type": "unknown", "mlat": [], "tisb": [], "messages": 41, "seen": 0.9, "rssi": -26.2}
{"hex": "47bfb3", "flight": "NSZ5333 ", "alt_baro": 38000, "alt_geom": 37650, "gs": 503.5, "tas": 454, "track": 210.7, "track_rate": 0.0, "roll": 0.2, "baro_rate": 0, "squawk": "2006", "emergency": "none", "category": "A3", "nav_qnh": 1013.6, "nav_altitude_mcp": 38016, "nav_altitude_fms": 38000, "nav_heading": 218.0, "version": 2, "nic_baro": 1, "nac_p": 11, "nac_v": 2, "sil": 3, "sil_type": "perhour", "gva": 2, "sda": 2, "mlat": [], "tisb": [], "messages": 133, "seen": 0.1, "rssi": -25.6}
{"hex": "8964e2", "alt_baro": 37000, "alt_geom": 37200, "gs": 489.6, "ias": 268, "tas": 472, "mach": 0.824, "track": 109.7, "track_rate": 0.03, "roll": 0.0, "mag_heading": 99.7, "baro_rate": 0, "geom_rate": 0, "squawk": "1171", "emergency": "none", "nav_qnh": 1013.6, "nav_altitude_mcp": 36992, "nav_heading": 99.8, "lat": 54.062256, "lon": -5.096479, "nic": 8, "rc": 186, "seen_pos": 1.3, "version": 0, "nic_baro": 1, "nac_p": 10, "nac_v": 1, "sil": 3, "sil_type": "unknown", "mlat": [], "tisb": [], "messages": 196, "seen": 0.2, "rssi": -23.6}
{"hex": "3c061d", "flight": "VJH983  ", "alt_baro": 39025, "alt_geom": 39250, "gs": 429.7, "tas": 488, "track": 47.7, "track_rate": 0.0, "roll": 0.2, "baro_rate": 0, "squawk": "6017", "category": "A2", "nav_qnh": 1013.6, "nav_altitude_mcp": 39008, "nav_altitude_fms": 39008, "nav_modes": ["autopilot", "althold", "tcas"], "lat": 55.392322, "lon": -5.428328, "nic": 8, "rc": 186, "seen_pos": 4.4, "version": 2, "nic_baro": 1, "nac_p": 11, "nac_v": 2, "sil": 3, "sil_type": "perhour", "gva": 2, "sda": 2, "mlat": [], "tisb": [], "messages": 101, "seen": 0.6, "rssi": -26.6}
{"hex": "4acb23", "mlat": [], "tisb": [], "messages": 33, "seen": 27.4, "rssi": -26.8}

Thank you for using {SCRIPT} - Andy Holmes / 2E0IJC"""


#==============================================================================================================
#==============================================================================================================
# getDistance: Calculate the distance from you QTH to the flight - in km's
def getDistance(flight_lat, flight_lon):
    dist_f = 0.0
    
    if (flight_lat):
        flight_coords = (flight_lat, flight_lon)
        distance = str(geopy.distance.geodesic(QTH, flight_coords))
        dist_f = float(f'{distance.strip(" km")}')
        dist_f = float(f'{dist_f: 7.1f}')
    
    return dist_f

# get Speed: Calculate the speed the aircraft is travelling
def getSpeed(flt_mach):
    fltSpeed = 0
    
    if (flt_mach):
        fltSpeed = int(flt_mach * MACH_SPD)
   
    return fltSpeed


# getData: call URL to get data - parse if SUCCESS: else exit.
def getData(flts, fltsExcld, fltsJson, fltStats):
        
    response = requests.get(DATA)                  # Get Flight Information from DATA

    if response.status_code == SUCCESS:               # Success
        
        flts.clear()                                   # Empty our lists to give us a clearn slate.
        fltsExcld.clear()
        fltsJson.clear()
        
        fltStats.clear()
        
        Positions       = 0
        NoPositions     = 0
        NumMLAT         = 0
        
        
        data = response.json()
        
        flight         = []
        
        highId         = 0
        highCl         = 0
        highest        = 0
        fastId         = 0
        fastCl         = 0
        fastest        = 0
        furtId         = 0
        furtCl         = 0
        furthest       = 0
        
        #NumMLAT        = 0
        
        for i in data['aircraft']:

            hx              = str(i.get('hex', DEFAULT))                       # This should NEVER be empty - but use DEFAULT value if it is!
            call            = i.get('flight', DEFAULT)                         # If Call Sign is empty - use DEFAULT value
            alt_baro        = i.get('alt_baro', 0)                             # If Altitude is empty - set to 0
            alt_geom        = i.get('alt_geom', 0)                             # If Altitude is empty - set to 0
            gs              = i.get('gs', None)
            ias             = i.get('ias', None)
            mach            = i.get('mach', 0)                                 # If Mach is empty - set to 0: this is used to calculate Speed
            
            speed           = getSpeed(mach)                                   # Calculate Speed
            
            hd              = int(i.get('track', 0))
            track_rate      = i.get('track_rate', None)
            roll            = i.get('roll', None)
            mag_head        = i.get('mag_heading', None)
            baro_rate       = i.get('baro_rate', 0)
            geom_rate       = i.get('geom_rate', 0)
            swk             = i.get('squawk', DEFAULT)
            emergency       = i.get('emergency', None)
            category        = i.get('category', UNKNOWN)
            nav_qnh         = i.get('nav_qnh', None)
            nav_altitude_mcp        = i.get('nav_altitude_mcp', None)
            nav_heading     = i.get('nav_heading', None)
            
            lat             = i.get('lat', None)
            if lat:
                lat = f'{lat:5.2f}'

            lon             = i.get('lon', None)
            if lon:
                lon = f'{lon:5.2f}'
            
            dist            = getDistance(lat, lon)                           # Calculate distance the flight is from QTH
            
            nic             = i.get('nic', None)
            rc              = i.get('rc', None)
            seen_pos        = i.get('seen_pos', None)
            version         = i.get('version', None)
            nic_baro        = i.get('nic_baro', None)
            nac_p           = i.get('nac_p', None)
            nac_v           = i.get('nac_v', None)
            sil             = i.get('sil', None)
            sil_type        = i.get('sil_type', None)
            gva             = i.get('gva', None)
            sda             = i.get('sda', None)
            mlat            = i.get('mlat', 'N')                  # MLAT is a list - needs further investigation to parse correctly.
            
            if mlat:                                            # If we have MLAT ....
                mlat = 'Y'                                      # translate to 'Y'
                NumMLAT = NumMLAT + 1
            else:
                mlat = 'N'
                
            tisb            = i.get('tisb', None)
            messages        = i.get('messages', None)
            seen            = i.get('seen', None)
            rssi            = i.get('rssi', None)
            
            # Check for Stats: Highest, Fastest, Furthest
            if alt_baro == "ground":
                alt_baro = 0                           # Ground prevents sorting by Altitude - it needs to be a number!
            else:
                if alt_baro > highest:
                    highId = hx
                    highCl = call
                    highest = alt_baro
                    
            
            if speed > fastest:
                fastId = hx
                fastCl = call
                fastest = speed
                
            
            if dist > furthest:
                furtId = hx
                furtCl = call
                furthest = dist
            
            # Add details to Flight List
            flight.append(hx)                       # 0
            flight.append(call)                     # 1
            flight.append(alt_baro)                 # 2    
            flight.append(int(alt_geom))
            flight.append(gs)
            flight.append(ias)
            flight.append(mach)        
            flight.append(speed)                    # 7
            flight.append(hd)                       # 8
            flight.append(track_rate)
            flight.append(roll)
            flight.append(mag_head)
            flight.append(baro_rate)
            flight.append(geom_rate)                # 13 Rate of ascent / descent?
            flight.append(swk)                      # 14
            flight.append(emergency)
            flight.append(category)                 # 16
            flight.append(nav_qnh)
            flight.append(nav_altitude_mcp)
            flight.append(nav_heading)
            flight.append(lat)                      # 20
            flight.append(lon)                      # 21
            flight.append(dist)                     # 22
            flight.append(nic)
            flight.append(rc)
            flight.append(seen_pos)
            flight.append(version)
            flight.append(nic_baro)
            flight.append(nac_p)
            flight.append(nac_v)
            flight.append(sil)
            flight.append(sil_type)
            flight.append(gva)
            flight.append(sda)
            flight.append(mlat)                      # 34
            flight.append(tisb)
            flight.append(messages)                  # 36
            flight.append(seen)                      # 37
            flight.append(rssi)                      # 38
            
            if hx in EXCLUDE:                           # Check if any of the flights need to be excluded
                fltsExcld.append(flight.copy())             # Add to Excluded Flights List
                #print(flight)                                 # debug
            else:
                flts.append(flight.copy())             # Add to Flights
                
                if lat:                                 # Check if Flight has a Latitude to determine flights with / without a position
                    Positions = Positions + 1
                else:
                    NoPositions = NoPositions + 1
            
            fltsJson.append(i)                           # Capture the JSON data raw

            flight.clear()    # We've parsed one Flight, logged and collected stats: clear down for next flight.

        # Update Stats
        fltStats.append(highId)                   # Highest
        fltStats.append(highCl)
        fltStats.append(highest)
        fltStats.append(fastId)                   # Fastest
        fltStats.append(fastCl)
        fltStats.append(fastest)
        fltStats.append(furtId)                   # Furthest
        fltStats.append(furtCl)
        fltStats.append(furthest)
        fltStats.append(Positions + NoPositions)
        fltStats.append(Positions)
        fltStats.append(len(fltsExcld))
        fltStats.append(NumMLAT)
    
    return response.status_code

def getFlightbyId(flights, id):
    pass

def getFlightbySquawk(Swk):
    pass

def getFlightbyCall(call):
    pass

def getHighest():
    pass

def getFastest():
    pass

def getFurthest():
    pass

def sortData(flights, sortBy, links, rev = False, extended = False):
    if sortBy in SORT:
        sortedFlights = sorted(flights, key=itemgetter(sortBy), reverse=rev)
        
        printFlights(sortedFlights, links, extended)
    else:
        print("We're sorry but we're unable to sort flights right now. Please try again later\n")

def printStats(fltStats, links = True, extended = False):
    print("Real Time Flight information:\n")
    output1 = f'\tTotal Aircraft: {fltStats[9]}\t\tHighest:  Id: {fltStats[0]}\tCall:  {fltStats[1]}\tAltitude: {fltStats[2]}m'                              # Formatting for Stats Update
    output2 = f'\tWith Positions: {fltStats[10]}\t\tFastest:  Id: {fltStats[3]}\tCall:  {fltStats[4]}\tSpeed:    {fltStats[5]}km/h'
    output3 = f'\tTotal Exluded:  {fltStats[11]}\t\tFurthest: Id: {fltStats[6]}\tCall:  {fltStats[7]}\tDistance: {fltStats[8]}km'
    output4 = f'\tTotal MLAT:     {fltStats[12]}'

    if links:
        output1 = output1 + f'\t{FLIGHT_LINK}{fltStats[0]}'
        output2 = output2 + f'\t{FLIGHT_LINK}{fltStats[3]}'
        output3 = output3 + f'\t{FLIGHT_LINK}{fltStats[6]}'
    
    print(output1)
    print(output2)
    print(output3)
    print(output4)



def printFlights(flts, incLinks = True, extdfmt = False):
    for i in flts:
        if extdfmt:
            output = f'Id: {i[0]}\tCall: {i[1]}\tSwk: {i[14]}\tAlt: {i[2]}ft\tSpd: {i[7]}km/h\tDist: {i[22]}km\tHd: {i[8]}\tCo-Ord: [{i[20]} / {i[21]}]\tCat: {i[16]}\tMLAT: {i[34]}\tMsg: {i[36]}\tSeen: {i[37]}\tRSSI: {i[38]}\n\tEmergency: {i[15]}\tMach: {i[6]}\tBaro Rate: {i[3]}\tGeom Rate: {i[4]}\tTrack Rate: {i[9]}\tRoll: {i[10]}\t'

        else:                                                          # Formatting for printing Flight Information
            output = f'Id: {i[0]}\tCall: {i[1]}\tSwk: {i[14]}\tAlt: {i[2]}ft\tSpd: {i[7]}km/h\tDist: {i[22]}km\tHd: {i[8]}\tCo-Ord: [{i[20]} / {i[21]}]\tCat: {i[16]}\tMLAT: {i[34]}\tRSSI: {i[38]}'
            
        if incLinks:
                output = output + f'\t{FLIGHT_LINK}{i[0]}'
        
        print(output)

    print("\n\n")



def printJson(fltsJson):
    for i in fltsJson:
        print(json.dumps(i))

def printHeader():
    pass

def printFooter():
    pass

def listCmds():
    print(CMD_STR)

def getHelp():
    print(HELP_STR1 + HELP_STR2)


flights       = []
excluded      = []
flightsJson    = []

Stats         = [HIGH_ID, HIGH_CALL, HIGHEST, FAST_ID, FAST_CALL, FASTEST, FURT_ID, FURT_CALL, FURTHEST, NUM_AIRCRAFT, NUM_NO_POSITIONS, NUM_EXLUDED, NUM_MLAT]

doMore     = True
isReverse  = False
incLinks   = True
extdfmt    = False

print(HEADER_INFO)




respCode = getData(flights, excluded, flightsJson, Stats)

if respCode == SUCCESS:
    
    print("Data retrieved:\n")
    printStats(Stats)
    
    while doMore:
        
        cmd = input("Cmd: ").lower()
        
        if cmd == QUIT:                                                     # Quit
            doMore = False
        if cmd == GET_DATA:                                                 # Get / Refresh the data
            respCode = getData(flights, excluded, flightsJson, Stats)
            
            if respCode == SUCCESS:                                         # Did we get the data?
                printStats(Stats)                                              # Yes - print the latest stats
            else:
                doMore = False                                                  # No - Quit: we can't do anything without data!
        elif cmd == STATS:                                                  # Stats: List Flight Stats
            printStats(Stats, incLinks)
        elif cmd == '':
            print(f'Aircraft with Positions: {len(flights)}\n')
            printFlights(flights, incLinks, extdfmt)
        elif cmd == FLIGHTS:                                                # Flights: List Flights unsorted
            print(f'Aircraft with Positions: {len(flights)}\n')
            printFlights(flights, incLinks, extdfmt)
        elif cmd == EXCLUDED:                                               # Excluded: List Excluded Flights
            print(f'Excluded Flights: {len(excluded)}\n')
            printFlights(excluded, incLinks, extdfmt)
        elif cmd == SORT_DISTANCE:                                          # Distance: Sort by Distance
            print("Flights Sorted by [Distance]\n")
            sortData(flights, DST, incLinks, isReverse, extdfmt)    
        elif cmd == SORT_ID:                                                # Id: Sort by Id / Hex
            print("Flights Sorted by [Id]\n")
            sortData(flights, HEX, incLinks, isReverse, extdfmt)
        elif cmd == SORT_CALL:                                              # Id: Sort by Id / Hex
            print("Flights Sorted by [Call Sign]\n")
            sortData(flights, CALL, incLinks, isReverse, extdfmt)
        elif cmd == SORT_ALT:                                               # Alt: Sort by Altitude
            print("Flights Sorted by [Altitude]\n")
            sortData(flights, ALT, incLinks, isReverse, extdfmt)
        elif cmd == SORT_VELOCITY:                                          # Velocity / Speed: Sort by Velocity
            print("Flights Sorted by [Speed]\n")
            sortData(flights, SPD, incLinks, isReverse, extdfmt)
        elif cmd == SORT_SQUAWK:                                            # Squawk: Sort by Squawk
            print("Flights Sorted by [Squawk]\n")
            sortData(flights, SWK, incLinks, isReverse, extdfmt)
        elif cmd == SORT_CATEGORY:                                          # Category / Aircraft Type
            print("Flights Sorted by [Category / Type]\n")
            sortData(flights, CAT, incLinks, isReverse, extdfmt)
        elif cmd == SORT_MLAT:                                          # MLAT
            print("Flights Sorted by [MLAT]\n")
            sortData(flights, MLT, incLinks, isReverse, extdfmt)
        elif cmd == SORT_RSSI:                                          # RSSI
            print("Flights Sorted by [RSSI]\n")
            sortData(flights, RSI, incLinks, isReverse, extdfmt)
        elif cmd == JSON:                                                   # Raw: Display Raw Flight Info: JSON Format
            printJson(flightsJson)
        elif cmd == INC_LINKS:
            if incLinks:
                incLinks = False
            else:
                incLinks = True
            print("Links is : " + str(incLinks))
        elif cmd == REVERSE:                                                # Reverse Order of Sort
            if isReverse:
                isReverse = False
            else:
                isReverse = True
            print("Reverse is: " + str(isReverse))
        elif cmd == EXTD_DATA:
            if extdfmt:
                extdfmt = False
            else:
                extdfmt = True
            print("Extended Format is: " + str(extdfmt))
        elif cmd == LIST_CMDS:                                              # ?: List available Commands
            listCmds()
        elif cmd == HELP:                                                   # Help: Display Help Information
            getHelp()
        else:
            print(f'Command not recognised - please try again:\n{COMMANDS}')



    
else:
     print(f"Sorry but we're unable to retrieve flight details right now [Error {respCode}]. \n Please try again later.")    

print(FOOTER_INFO)
print(TRAILER_INFO)









    
       
        


