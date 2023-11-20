# feederReader
reads, displays and sorts tar1090 aircraft.json ADSB data

## Setup: 
1. Update the script with your location: Latitude / Longitude - search for 'SET'.
1. Update the URL to point to your tar10190 data. 
	- Eg URL      = "http://radiopi/tar1090/"
	- Eg URL      = "http://localhost/tar1090/"

## Usage:
This script takes real-time Aircraft ADSB output from tar10190/data/aircraft.json, parses it and displays it.
It can help in understanding more about the information transmitted in ADSB transmissions.

The aircraft.json data is read into two lists, formatted and the raw JSON data. As the data is parsed, the script
also captures stats: **s**

	Cmd: s
	Real Time Flight information:

		Total Aircraft: 57		Highest:  Id: 4010ee	Call:  XXXX	      Altitude: 48100m	  http://radiopi/tar1090/?icao=4010ee
		With Positions: 42		Fastest:  Id: 4bb183	Call:  THY29M  	  Speed:    1012km/h	http://radiopi/tar1090/?icao=4bb183
		Total Exluded:  3		Furthest: Id: 44061b	Call:  XXXX	        Distance: 392.5km	  http://radiopi/tar1090/?icao=44061b
		Total MLAT:     8

The URL link can be included / excluded using the l command:

	Cmd: l
	Links is : False
	Cmd: s
	Real Time Flight information:

		Total Aircraft: 57		Highest:  Id: 4010ee	Call:  XXXX	    Altitude: 48100m
		With Positions: 42		Fastest:  Id: 4bb183	Call:  THY29M  	Speed:    1012km/h
		Total Exluded:  3		  Furthest: Id: 44061b	Call:  XXXX	    Distance: 392.5km
		Total MLAT:     8

Flights are displayed by using the **f** command:

	Cmd: f
	Aircraft with Positions: 57

	Id: 407f6e	Call: ABV4FS  	Swk: 5155	Alt: 22975ft	Spd: 700km/h	Dist: 245.3km	Hd: 126	Co-Ord: [53.98 / -4.88]	Cat: XX	MLAT: N	RSSI: -24.6
	Id: 406c72	Call: EZY780W 	Swk: 6306	Alt: 25275ft	Spd: 830km/h	Dist: 290.5km	Hd: 320	Co-Ord: [52.46 / -0.78]	Cat: A3	MLAT: N	RSSI: -20.4
	Id: 4ca7b9	Call: RYR95YZ 	Swk: 0474	Alt: 3725ft	    Spd: 388km/h	Dist: 69.1km	Hd: 227	Co-Ord: [54.41 / -1.62]	Cat: A3	MLAT: N	RSSI: -4.4
	Id: 4cad9f	Call: XXXX	    Swk: XXXX	Alt: 46900ft	Spd: 0km/h	    Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: A2	MLAT: N	RSSI: -27.6
	Id: 4ca625	Call: XXXX	    Swk: 5166	Alt: 0ft	    Spd: 0km/h	    Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: XX	MLAT: N	RSSI: -29.4
	Id: 4009da	Call: XXXX	    Swk: XXXX	Alt: 27000ft	Spd: 960km/h	Dist: 0.0km	    Hd: 0	Co-Ord: [None / None]	Cat: XX	MLAT: N	RSSI: -14.7
	Id: 407ac1	Call: TOM30T  	Swk: 7662	Alt: 35875ft	Spd: 960km/h	Dist: 326.3km	Hd: 44	Co-Ord: [52.45 / -3.90]	Cat: A3	MLAT: N	RSSI: -26.8


Extended information can be displayed using the **x** command:

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
	i	Id / Hex Code		d	Distance	v	Velocity / Speed
	c	Call Sign		k	Squawk Code	t	Aircraft Type
	m	MLAT			^	RSSI - Signal Strength

The r command can be used to Reverse the sort order.

	Cmd: r
	Reverse is: True
	Cmd: i
	Flights Sorted by [Id]
	
	Id: a57ad0	Call: GTI8298 	Swk: 2207	Alt: 37000ft	Spd: 988km/h	Dist: 178.1km	Hd: 131	Co-Ord: [53.60 / -0.32]	Cat: A5	MLAT: N	RSSI: -20.0
	Id: 4d2387	Call: RYR99HM 	Swk: 7667	Alt: 29000ft	Spd: 796km/h	Dist: 242.4km	Hd: 101	Co-Ord: [53.06 / -3.13]	Cat: A3	MLAT: N	RSSI: -15.2
	Id: 4d22c3	Call: RYR57KK 	Swk: 2264	Alt: 24075ft	Spd: 820km/h	Dist: 191.0km	Hd: 104	Co-Ord: [53.33 / -1.15]	Cat: A3	MLAT: N	RSSI: -14.4
	Id: 4cc4c5	Call: ABD387  	Swk: 2217	Alt: 35000ft	Spd: 998km/h	Dist: 229.4km	Hd: 130	Co-Ord: [53.44 / -3.79]	Cat: A5	MLAT: N	RSSI: -16.4


The data can be refreshed using the **g** command and updates the stats, formatted and raw JSON data.

The raw JSON data can be viewed using the **j** command for a better understanding of the data.

	Cmd: j
	{"hex": "80153d", "alt_baro": 35000, "alt_geom": 35200, "gs": 532.9, "track": 124.9, "baro_rate": 0, "squawk": "2221", "lat": 55.785129, "lon": -4.924793, "nic": 8, "rc": 186, "seen_pos": 12.2, "version": 0, "nac_p": 8, "nac_v": 1, "sil": 2, "sil_type": "unknown", "mlat": [], "tisb": [], "messages": 41, "seen": 0.9, "rssi": -26.2}
	{"hex": "47bfb3", "flight": "NSZ5333 ", "alt_baro": 38000, "alt_geom": 37650, "gs": 503.5, "tas": 454, "track": 210.7, "track_rate": 0.0, "roll": 0.2, "baro_rate": 0, "squawk": "2006", "emergency": "none", "category": "A3", "nav_qnh": 1013.6, "nav_altitude_mcp": 38016, "nav_altitude_fms": 38000, "nav_heading": 218.0, "version": 2, "nic_baro": 1, "nac_p": 11, "nac_v": 2, "sil": 3, "sil_type": "perhour", "gva": 2, "sda": 2, "mlat": [], "tisb": [], "messages": 133, "seen": 0.1, "rssi": -25.6}
	{"hex": "8964e2", "alt_baro": 37000, "alt_geom": 37200, "gs": 489.6, "ias": 268, "tas": 472, "mach": 0.824, "track": 109.7, "track_rate": 0.03, "roll": 0.0, "mag_heading": 99.7, "baro_rate": 0, "geom_rate": 0, "squawk": "1171", "emergency": "none", "nav_qnh": 1013.6, "nav_altitude_mcp": 36992, "nav_heading": 99.8, "lat": 54.062256, "lon": -5.096479, "nic": 8, "rc": 186, "seen_pos": 1.3, "version": 0, "nic_baro": 1, "nac_p": 10, "nac_v": 1, "sil": 3, "sil_type": "unknown", "mlat": [], "tisb": [], "messages": 196, "seen": 0.2, "rssi": -23.6}
	{"hex": "3c061d", "flight": "VJH983  ", "alt_baro": 39025, "alt_geom": 39250, "gs": 429.7, "tas": 488, "track": 47.7, "track_rate": 0.0, "roll": 0.2, "baro_rate": 0, "squawk": "6017", "category": "A2", "nav_qnh": 1013.6, "nav_altitude_mcp": 39008, "nav_altitude_fms": 39008, "nav_modes": ["autopilot", "althold", "tcas"], "lat": 55.392322, "lon": -5.428328, "nic": 8, "rc": 186, "seen_pos": 4.4, "version": 2, "nic_baro": 1, "nac_p": 11, "nac_v": 2, "sil": 3, "sil_type": "perhour", "gva": 2, "sda": 2, "mlat": [], "tisb": [], "messages": 101, "seen": 0.6, "rssi": -26.6}
	{"hex": "4acb23", "mlat": [], "tisb": [], "messages": 33, "seen": 27.4, "rssi": -26.8}

Thank you for using FeederReader - Andy Holmes / 2E0IJC
