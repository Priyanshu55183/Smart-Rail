"""
Seed Data — 75 Train Routes with Full Schedules
=================================================
Each train has realistic stop-by-stop timings, day offsets,
halt durations, and distances.

Routes overlap at junction stations — this creates CONNECTION
OPPORTUNITIES for the Dijkstra algorithm.

Example connection the graph will discover:
  Train 12627 (SBC → NDLS) stops at SC (Secunderabad)
  Train 12723 (HYB → NDLS) also departs from SC
  → Dijkstra finds: SBC → SC (Train 12627) → SC → NDLS (Train 12723)

Each train is defined as:
  (train_number, name, type, runs_on_days, stops_list)

Each stop: (station_code, arrival, departure, day_offset, halt_min, distance_km)
  - arrival=None for first stop (train originates)
  - departure=None for last stop (train terminates)
  - day_offset: 0=day1, 1=day2, etc. (handles overnight)
"""

TRAINS_DATA = [
    # ═══════════════════════════════════════════════════════
    # CORRIDOR 1: BENGALURU ↔ NEW DELHI (via Hyderabad / Guntakal)
    # ═══════════════════════════════════════════════════════
    
    # Train 1: Karnataka Express (SBC → NDLS) — 42h journey
    {
        "number": "12627",
        "name": "Karnataka Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", None, "21:40", 0, 0, 0),
            ("YPR", "22:05", "22:10", 0, 5, 8),
            ("GTL", "04:30", "04:40", 1, 10, 476),
            ("SC", "09:15", "09:30", 1, 15, 785),
            ("NGP", "18:50", "19:05", 1, 15, 1371),
            ("BPL", "01:30", "01:45", 2, 15, 1781),
            ("JHS", "05:10", "05:15", 2, 5, 2000),
            ("AGC", "08:00", "08:10", 2, 10, 2198),
            ("NDLS", "11:35", None, 2, 0, 2444),
        ]
    },
    
    # Train 2: Rajdhani Express (SBC → NDLS) — Premium, faster
    {
        "number": "22691",
        "name": "SBC Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Wed,Fri,Sun",
        "stops": [
            ("SBC", "20:00", "20:00", 0, 0, 0),
            ("GTL", "02:30", "02:35", 1, 5, 476),
            ("SC", "06:00", "06:15", 1, 15, 785),
            ("NGP", "14:30", "14:40", 1, 10, 1371),
            ("BPL", "20:15", "20:25", 1, 10, 1781),
            ("JHS", "00:30", "00:35", 2, 5, 2000),
            ("AGC", "03:40", "03:45", 2, 5, 2198),
            ("NZM", "06:05", None, 2, 0, 2444),
        ]
    },
    
    # Train 3: YPR-NDLS AC Express
    {
        "number": "12649",
        "name": "Karnataka Sampark Kranti",
        "type": "SUPERFAST",
        "runs_on": "Tue,Thu,Sat",
        "stops": [
            ("YPR", "21:15", "21:15", 0, 0, 0),
            ("GTL", "04:00", "04:05", 1, 5, 468),
            ("KOTA", "18:30", "18:35", 1, 5, 1550),
            ("SWM", "19:50", "19:55", 1, 5, 1630),
            ("NZM", "05:15", None, 2, 0, 2368),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 2: HYDERABAD ↔ NEW DELHI
    # ═══════════════════════════════════════════════════════
    
    # Train 4: Telangana Express
    {
        "number": "12723",
        "name": "Telangana Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SC", "06:25", "06:25", 0, 0, 0),
            ("NGP", "15:45", "16:00", 0, 15, 586),
            ("BPL", "23:40", "23:55", 0, 15, 996),
            ("JHS", "04:40", "04:50", 1, 10, 1215),
            ("AGC", "08:05", "08:15", 1, 10, 1413),
            ("NDLS", "12:30", None, 1, 0, 1659),
        ]
    },
    
    # Train 5: Dakshin Express (HYB → NDLS)
    {
        "number": "12721",
        "name": "Dakshin Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HYB", "19:05", "19:05", 0, 0, 0),
            ("SC", "19:35", "19:50", 0, 15, 12),
            ("NGP", "05:30", "05:45", 1, 15, 598),
            ("BPL", "14:20", "14:35", 1, 15, 1008),
            ("JHS", "19:40", "19:50", 1, 10, 1227),
            ("AGC", "23:00", "23:10", 1, 10, 1425),
            ("MTJ", "00:10", "00:15", 2, 5, 1483),
            ("NDLS", "05:30", None, 2, 0, 1659),
        ]
    },
    
    # Train 6: AP Express (SC → NDLS) — another timing option
    {
        "number": "12707",
        "name": "Andhra Pradesh Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SC", "17:55", "17:55", 0, 0, 0),
            ("BZA", "23:45", "23:55", 0, 10, 290),
            ("NGP", "09:10", "09:25", 1, 15, 586),
            ("BPL", "16:45", "17:00", 1, 15, 996),
            ("JHS", "22:50", "23:00", 1, 10, 1215),
            ("AGC", "02:20", "02:30", 2, 10, 1413),
            ("NDLS", "06:15", None, 2, 0, 1659),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 3: BENGALURU ↔ HYDERABAD (SHORT, for connections)
    # ═══════════════════════════════════════════════════════
    
    # Train 7: SBC-SC Intercity
    {
        "number": "12785",
        "name": "SBC-SC Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "06:30", "06:30", 0, 0, 0),
            ("DMM", "10:30", "10:35", 0, 5, 257),
            ("GTL", "12:00", "12:10", 0, 10, 361),
            ("SC", "18:20", None, 0, 0, 785),
        ]
    },
    
    # Train 8: YPR-SC Express (afternoon departure)
    {
        "number": "12787",
        "name": "YPR-SC Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("YPR", "14:20", "14:20", 0, 0, 0),
            ("GTL", "20:45", "20:55", 0, 10, 468),
            ("SC", "03:10", None, 1, 0, 793),
        ]
    },
    
    # ═══════════════════════════════════════════════════════
    # CORRIDOR 4: MUMBAI ↔ NEW DELHI (Western)
    # ═══════════════════════════════════════════════════════
    
    # Train 9: Mumbai Rajdhani
    {
        "number": "12951",
        "name": "Mumbai Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BCT", "17:00", "17:00", 0, 0, 0),
            ("BRC", "20:58", "21:03", 0, 5, 392),
            ("RTM", "01:38", "01:40", 1, 2, 750),
            ("KOTA", "04:20", "04:25", 1, 5, 980),
            ("NDLS", "08:35", None, 1, 0, 1384),
        ]
    },
    
    # Train 10: August Kranti Rajdhani
    {
        "number": "12953",
        "name": "August Kranti Rajdhani",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BCT", "17:40", "17:40", 0, 0, 0),
            ("ST", "21:28", "21:30", 0, 2, 263),
            ("BRC", "23:13", "23:18", 0, 5, 392),
            ("KOTA", "05:10", "05:15", 1, 5, 980),
            ("NZM", "10:55", None, 1, 0, 1384),
        ]
    },
    
    # Train 11: Paschim Express
    {
        "number": "12925",
        "name": "Paschim Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BCT", "11:25", "11:25", 0, 0, 0),
            ("BRC", "15:35", "15:45", 0, 10, 392),
            ("RTM", "22:30", "22:40", 0, 10, 750),
            ("KOTA", "01:40", "01:50", 1, 10, 980),
            ("SWM", "03:10", "03:15", 1, 5, 1060),
            ("JP", "05:15", "05:30", 1, 15, 1175),
            ("NDLS", "11:00", None, 1, 0, 1384),
        ]
    },
    
    # Train 12: Gujarat Mail (BCT → NDLS via ADI)
    {
        "number": "12901",
        "name": "Gujarat Mail",
        "type": "MAIL",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BCT", "22:05", "22:05", 0, 0, 0),
            ("ST", "01:40", "01:45", 1, 5, 263),
            ("BRC", "04:05", "04:15", 1, 10, 392),
            ("ADI", "06:30", "06:45", 1, 15, 493),
            ("ABR", "10:00", "10:05", 1, 5, 700),
            ("NDLS", "04:30", None, 2, 0, 1384),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 5: MUMBAI ↔ CHENNAI
    # ═══════════════════════════════════════════════════════
    
    # Train 13: Mumbai-Chennai Express
    {
        "number": "11041",
        "name": "Mumbai-Chennai Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("CSMT", "21:00", "21:00", 0, 0, 0),
            ("PUNE", "00:20", "00:30", 1, 10, 192),
            ("SRE", "05:20", "05:30", 1, 10, 456),
            ("GTL", "14:00", "14:15", 1, 15, 793),
            ("JTJ", "20:00", "20:10", 1, 10, 1083),
            ("MAS", "00:10", None, 2, 0, 1279),
        ]
    },
    
    # Train 14: Dadar-Chennai Express
    {
        "number": "11043",
        "name": "Dadar-Chennai Express",
        "type": "EXPRESS",
        "runs_on": "Tue,Thu,Sun",
        "stops": [
            ("LTT", "14:25", "14:25", 0, 0, 0),
            ("PUNE", "18:00", "18:10", 0, 10, 171),
            ("SRE", "23:15", "23:25", 0, 10, 435),
            ("WADI", "02:00", "02:10", 1, 10, 580),
            ("GTL", "07:20", "07:35", 1, 15, 772),
            ("RU", "15:05", "15:10", 1, 5, 1073),
            ("MAS", "18:50", None, 1, 0, 1258),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 6: KOLKATA ↔ NEW DELHI
    # ═══════════════════════════════════════════════════════
    
    # Train 15: Howrah Rajdhani
    {
        "number": "12301",
        "name": "Howrah Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HWH", "16:55", "16:55", 0, 0, 0),
            ("DHN", "20:13", "20:15", 0, 2, 265),
            ("GY", "22:40", "22:42", 0, 2, 453),
            ("MGS", "00:40", "00:50", 1, 10, 564),
            ("CNB", "04:55", "05:00", 1, 5, 848),
            ("NDLS", "09:55", None, 1, 0, 1447),
        ]
    },
    
    # Train 16: Sealdah Rajdhani
    {
        "number": "12313",
        "name": "Sealdah Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Wed,Thu,Sat",
        "stops": [
            ("SDAH", "16:10", "16:10", 0, 0, 0),
            ("DHN", "20:27", "20:29", 0, 2, 276),
            ("GY", "22:55", "22:57", 0, 2, 464),
            ("MGS", "01:00", "01:05", 1, 5, 575),
            ("CNB", "05:30", "05:35", 1, 5, 859),
            ("NDLS", "10:05", None, 1, 0, 1458),
        ]
    },
    
    # Train 17: Poorva Express
    {
        "number": "12303",
        "name": "Poorva Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HWH", "20:05", "20:05", 0, 0, 0),
            ("ASN", "23:05", "23:10", 0, 5, 203),
            ("DHN", "00:25", "00:30", 1, 5, 265),
            ("GY", "04:10", "04:15", 1, 5, 453),
            ("MGS", "05:40", "05:55", 1, 15, 564),
            ("ALD", "07:45", "07:55", 1, 10, 676),
            ("CNB", "10:50", "11:00", 1, 10, 848),
            ("NDLS", "17:25", None, 1, 0, 1447),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 7: KOLKATA ↔ CHENNAI (East Coast)
    # ═══════════════════════════════════════════════════════
    
    # Train 18: Coromandel Express
    {
        "number": "12841",
        "name": "Coromandel Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HWH", "14:50", "14:50", 0, 0, 0),
            ("KGP", "17:11", "17:13", 0, 2, 113),
            ("BBS", "22:40", "22:50", 0, 10, 440),
            ("VSKP", "03:50", "04:00", 1, 10, 756),
            ("BZA", "10:10", "10:20", 1, 10, 1090),
            ("MAS", "17:15", None, 1, 0, 1663),
        ]
    },
    
    # Train 19: Falaknuma Express (SC → HWH)
    {
        "number": "12703",
        "name": "Falaknuma Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SC", "15:50", "15:50", 0, 0, 0),
            ("BZA", "21:10", "21:20", 0, 10, 290),
            ("VSKP", "03:30", "03:45", 1, 15, 606),
            ("BBS", "08:40", "08:50", 1, 10, 932),
            ("KGP", "15:35", "15:40", 1, 5, 1319),
            ("HWH", "18:45", None, 1, 0, 1432),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 8: MUMBAI ↔ KOLKATA (via Nagpur)
    # ═══════════════════════════════════════════════════════
    
    # Train 20: Gitanjali Express
    {
        "number": "12859",
        "name": "Gitanjali Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("CSMT", "06:00", "06:00", 0, 0, 0),
            ("BSL", "12:05", "12:15", 0, 10, 424),
            ("NGP", "18:40", "18:55", 0, 15, 839),
            ("R", "00:50", "01:00", 1, 10, 1125),
            ("TATA", "09:00", "09:10", 1, 10, 1568),
            ("KGP", "11:10", "11:15", 1, 5, 1694),
            ("HWH", "14:30", None, 1, 0, 1867),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 9: CHENNAI ↔ NEW DELHI
    # ═══════════════════════════════════════════════════════
    
    # Train 21: Tamil Nadu Express
    {
        "number": "12621",
        "name": "Tamil Nadu Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("MAS", "22:00", "22:00", 0, 0, 0),
            ("JTJ", "00:55", "01:00", 1, 5, 212),
            ("GTL", "05:00", "05:05", 1, 5, 406),
            ("SC", "11:55", "12:05", 1, 10, 694),
            ("NGP", "20:30", "20:45", 1, 15, 1280),
            ("BPL", "05:30", "05:45", 2, 15, 1690),
            ("JHS", "09:50", "10:00", 2, 10, 1909),
            ("AGC", "13:10", "13:20", 2, 10, 2107),
            ("NDLS", "07:00", None, 3, 0, 2182),
        ]
    },
    
    # Train 22: GT Express (MAS → NDLS)
    {
        "number": "12615",
        "name": "Grand Trunk Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("MAS", "18:45", "18:45", 0, 0, 0),
            ("RU", "20:50", "20:55", 0, 5, 133),
            ("GTL", "02:10", "02:20", 1, 10, 406),
            ("SC", "08:25", "08:40", 1, 15, 694),
            ("NGP", "17:25", "17:40", 1, 15, 1280),
            ("BPL", "02:45", "03:00", 2, 15, 1690),
            ("JHS", "07:35", "07:45", 2, 10, 1909),
            ("AGC", "10:40", "10:50", 2, 10, 2107),
            ("NDLS", "18:00", None, 2, 0, 2182),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 10: BENGALURU ↔ CHENNAI
    # ═══════════════════════════════════════════════════════
    
    # Train 23: Shatabdi Express (SBC → MAS)
    {
        "number": "12007",
        "name": "SBC-MAS Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("SBC", "06:00", "06:00", 0, 0, 0),
            ("JTJ", "08:48", "08:50", 0, 2, 196),
            ("MAS", "11:00", None, 0, 0, 362),
        ]
    },
    
    # Train 24: Lalbagh Express (SBC → MAS)
    {
        "number": "12607",
        "name": "Lalbagh Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "06:20", "06:20", 0, 0, 0),
            ("JTJ", "09:20", "09:22", 0, 2, 196),
            ("MAS", "11:30", None, 0, 0, 362),
        ]
    },
    
    # Train 25: Brindavan Express (SBC → MAS, afternoon)
    {
        "number": "12639",
        "name": "Brindavan Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "14:20", "14:20", 0, 0, 0),
            ("JTJ", "17:10", "17:12", 0, 2, 196),
            ("MAS", "19:25", None, 0, 0, 362),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 11: AHMEDABAD ↔ NEW DELHI
    # ═══════════════════════════════════════════════════════
    
    # Train 26: Ashram Express
    {
        "number": "12915",
        "name": "Ashram Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("ADI", "16:00", "16:00", 0, 0, 0),
            ("BRC", "17:40", "17:45", 0, 5, 100),
            ("RTM", "21:50", "21:55", 0, 5, 361),
            ("KOTA", "01:20", "01:25", 1, 5, 585),
            ("SWM", "03:00", "03:02", 1, 2, 665),
            ("JP", "05:40", "05:50", 1, 10, 779),
            ("NDLS", "10:40", None, 1, 0, 942),
        ]
    },
    
    # Train 27: ADI-NDLS Rajdhani
    {
        "number": "12957",
        "name": "ADI Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("ADI", "19:40", "19:40", 0, 0, 0),
            ("BRC", "21:10", "21:13", 0, 3, 100),
            ("KOTA", "03:40", "03:45", 1, 5, 585),
            ("NDLS", "08:35", None, 1, 0, 942),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 12: PUNE ↔ NEW DELHI  
    # ═══════════════════════════════════════════════════════
    
    # Train 28: Pune-NDLS Duronto
    {
        "number": "12263",
        "name": "Pune Duronto Express",
        "type": "DURONTO",
        "runs_on": "Mon,Thu,Sat",
        "stops": [
            ("PUNE", "15:35", "15:35", 0, 0, 0),
            ("BSL", "22:55", "23:05", 0, 10, 382),
            ("BPL", "05:35", "05:45", 1, 10, 782),
            ("AGC", "13:20", "13:30", 1, 10, 1280),
            ("NZM", "16:55", None, 1, 0, 1504),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 13: BENGALURU ↔ MUMBAI
    # ═══════════════════════════════════════════════════════
    
    # Train 29: Udyan Express
    {
        "number": "11301",
        "name": "Udyan Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "20:20", "20:20", 0, 0, 0),
            ("UBL", "06:30", "06:40", 1, 10, 432),
            ("GOA", "10:30", "10:35", 1, 5, 580),
            ("PUNE", "21:15", "21:30", 1, 15, 985),
            ("CSMT", "01:05", None, 2, 0, 1177),
        ]
    },
    
    # Train 30: SBC-BCT Superfast
    {
        "number": "12677",
        "name": "KSR Bengaluru-Ernakulam SF",
        "type": "SUPERFAST",
        "runs_on": "Tue,Fri,Sun",
        "stops": [
            ("SBC", "18:15", "18:15", 0, 0, 0),
            ("MYS", "21:00", "21:05", 0, 5, 139),
            ("MQ", "05:20", "05:25", 1, 5, 380),
            ("ERS", "12:15", None, 1, 0, 600),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 14: JAIPUR ↔ OTHER CITIES
    # ═══════════════════════════════════════════════════════
    
    # Train 31: Jaipur-Mumbai Superfast
    {
        "number": "12955",
        "name": "JP-BCT Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("JP", "14:00", "14:00", 0, 0, 0),
            ("AII", "16:10", "16:15", 0, 5, 135),
            ("ADI", "23:15", "23:30", 0, 15, 498),
            ("BRC", "01:15", "01:20", 1, 5, 598),
            ("ST", "03:45", "03:50", 1, 5, 727),
            ("BCT", "08:20", None, 1, 0, 1105),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 15: LUCKNOW ↔ OTHER CITIES
    # ═══════════════════════════════════════════════════════
    
    # Train 32: Pushpak Express (LKO → CSMT)
    {
        "number": "12533",
        "name": "Pushpak Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("LKO", "22:50", "22:50", 0, 0, 0),
            ("CNB", "00:30", "00:35", 1, 5, 82),
            ("JHS", "04:50", "04:55", 1, 5, 307),
            ("BPL", "09:55", "10:10", 1, 15, 520),
            ("ET", "12:05", "12:10", 1, 5, 615),
            ("BSL", "16:45", "16:55", 1, 10, 843),
            ("MMR", "19:55", "20:00", 1, 5, 990),
            ("CSMT", "00:50", None, 2, 0, 1380),
        ]
    },
    
    # Train 33: Lucknow Shatabdi (LKO → NDLS)
    {
        "number": "12003",
        "name": "Lucknow Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("LKO", "06:10", "06:10", 0, 0, 0),
            ("CNB", "07:22", "07:24", 0, 2, 82),
            ("AGC", "10:00", "10:02", 0, 2, 348),
            ("NDLS", "12:20", None, 0, 0, 512),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 16: BENGALURU ↔ KOLKATA (via HYB/BZA)
    # ═══════════════════════════════════════════════════════
    
    # Train 34: SBC-HWH Express
    {
        "number": "12245",
        "name": "Yesvantpur-Howrah Duronto",
        "type": "DURONTO",
        "runs_on": "Wed,Sat",
        "stops": [
            ("YPR", "06:15", "06:15", 0, 0, 0),
            ("GTL", "12:05", "12:10", 0, 5, 468),
            ("SC", "17:30", "17:45", 0, 15, 793),
            ("BZA", "22:00", "22:10", 0, 10, 1083),
            ("VSKP", "03:50", "04:00", 1, 10, 1399),
            ("BBS", "08:50", "09:00", 1, 10, 1725),
            ("KGP", "14:55", "15:00", 1, 5, 2112),
            ("HWH", "18:30", None, 1, 0, 2225),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 17: MUMBAI ↔ HYDERABAD
    # ═══════════════════════════════════════════════════════
    
    # Train 35: Hussainsagar Express
    {
        "number": "12701",
        "name": "Hussainsagar Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("CSMT", "21:50", "21:50", 0, 0, 0),
            ("PUNE", "01:10", "01:20", 1, 10, 192),
            ("SRE", "06:15", "06:20", 1, 5, 456),
            ("WADI", "08:50", "09:00", 1, 10, 580),
            ("GTL", "12:10", "12:20", 1, 10, 698),
            ("SC", "18:00", None, 1, 0, 793),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # CORRIDOR 18: ADDITIONAL ROUTES FOR MORE CONNECTIONS
    # ═══════════════════════════════════════════════════════
    
    # Train 36: Patna-NDLS Jan Shatabdi
    {
        "number": "12561",
        "name": "Patna Jan Shatabdi Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("PNBE", "05:30", "05:30", 0, 0, 0),
            ("MGS", "07:00", "07:05", 0, 5, 108),
            ("ALD", "09:10", "09:15", 0, 5, 220),
            ("CNB", "12:20", "12:25", 0, 5, 392),
            ("AGC", "15:40", "15:45", 0, 5, 590),
            ("NDLS", "19:05", None, 0, 0, 818),
        ]
    },
    
    # Train 37: Varanasi-NDLS Superfast
    {
        "number": "12559",
        "name": "Varanasi Shiv Ganga Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BSB", "19:00", "19:00", 0, 0, 0),
            ("ALD", "21:25", "21:30", 0, 5, 126),
            ("CNB", "00:15", "00:25", 1, 10, 298),
            ("LKO", "03:20", "03:25", 1, 5, 378),
            ("NDLS", "09:15", None, 1, 0, 764),
        ]
    },
    
    # Train 38: Bhopal Shatabdi (BPL → NDLS)
    {
        "number": "12001",
        "name": "Bhopal Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("BPL", "06:00", "06:00", 0, 0, 0),
            ("JHS", "09:55", "09:58", 0, 3, 219),
            ("AGC", "12:50", "12:55", 0, 5, 417),
            ("NDLS", "15:45", None, 0, 0, 690),
        ]
    },
    
    # Train 39: Nagpur-Mumbai Duronto
    {
        "number": "12289",
        "name": "Nagpur Duronto Express",
        "type": "DURONTO",
        "runs_on": "Mon,Wed,Fri",
        "stops": [
            ("NGP", "20:15", "20:15", 0, 0, 0),
            ("BSL", "01:20", "01:25", 1, 5, 400),
            ("MMR", "05:15", "05:20", 1, 5, 600),
            ("CSMT", "09:00", None, 1, 0, 839),
        ]
    },
    
    # Train 40: BZA-SC Intercity
    {
        "number": "12733",
        "name": "BZA-SC Intercity Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BZA", "06:00", "06:00", 0, 0, 0),
            ("GNT", "06:40", "06:42", 0, 2, 35),
            ("SC", "12:05", None, 0, 0, 290),
        ]
    },
    
    # Train 41: VSKP-SC Godavari Express
    {
        "number": "12727",
        "name": "Godavari Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("VSKP", "17:30", "17:30", 0, 0, 0),
            ("BZA", "00:20", "00:30", 1, 10, 360),
            ("SC", "06:30", None, 1, 0, 650),
        ]
    },

    # Train 42: GTL-SC Express
    {
        "number": "17001",
        "name": "Guntakal-SC Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("GTL", "20:15", "20:15", 0, 0, 0),
            ("SC", "04:30", None, 1, 0, 324),
        ]
    },

    # Train 43: BBS-NDLS Rajdhani
    {
        "number": "22811",
        "name": "BBS Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Thu,Sat",
        "stops": [
            ("BBS", "17:00", "17:00", 0, 0, 0),
            ("R", "22:55", "23:05", 0, 10, 473),
            ("NGP", "04:00", "04:10", 1, 10, 756),
            ("BPL", "10:10", "10:20", 1, 10, 1166),
            ("JHS", "14:15", "14:20", 1, 5, 1385),
            ("AGC", "17:20", "17:25", 1, 5, 1583),
            ("NDLS", "21:00", None, 1, 0, 1829),
        ]
    },

    # Train 44: NZM-SC Duronto
    {
        "number": "12285",
        "name": "NZM-SC Duronto Express",
        "type": "DURONTO",
        "runs_on": "Tue,Fri,Sun",
        "stops": [
            ("NZM", "20:30", "20:30", 0, 0, 0),
            ("AGC", "23:00", "23:05", 0, 5, 200),
            ("JHS", "02:15", "02:20", 1, 5, 418),
            ("BPL", "07:20", "07:30", 1, 10, 631),
            ("NGP", "14:10", "14:20", 1, 10, 1047),
            ("SC", "22:30", None, 1, 0, 1633),
        ]
    },

    # Train 45: MAS-SC Express
    {
        "number": "12759",
        "name": "Charminar Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("MAS", "18:40", "18:40", 0, 0, 0),
            ("RU", "20:30", "20:35", 0, 5, 133),
            ("GTL", "02:00", "02:10", 1, 10, 406),
            ("SC", "08:30", None, 1, 0, 694),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # MORE TRAINS FOR RICHER CONNECTIONS
    # ═══════════════════════════════════════════════════════

    # Train 46: Jaipur-SC Express
    {
        "number": "12731",
        "name": "JP-SC Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Wed,Fri,Sun",
        "stops": [
            ("JP", "16:30", "16:30", 0, 0, 0),
            ("KOTA", "20:15", "20:20", 0, 5, 200),
            ("BPL", "05:30", "05:40", 1, 10, 550),
            ("NGP", "14:20", "14:35", 1, 15, 964),
            ("SC", "01:30", None, 2, 0, 1550),
        ]
    },
    
    # Train 47: SC-SBC Intercity (evening)
    {
        "number": "12786",
        "name": "SC-SBC Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SC", "20:35", "20:35", 0, 0, 0),
            ("GTL", "03:55", "04:05", 1, 10, 324),
            ("DMM", "05:30", "05:35", 1, 5, 428),
            ("SBC", "10:50", None, 1, 0, 785),
        ]
    },
    
    # Train 48: ADI-SBC Express (via Pune)
    {
        "number": "16507",
        "name": "ADI-SBC Express",
        "type": "EXPRESS",
        "runs_on": "Tue,Thu,Sat",
        "stops": [
            ("ADI", "05:30", "05:30", 0, 0, 0),
            ("BRC", "07:15", "07:20", 0, 5, 100),
            ("PUNE", "16:00", "16:15", 0, 15, 570),
            ("SRE", "20:30", "20:40", 0, 10, 768),
            ("GTL", "04:10", "04:20", 1, 10, 1005),
            ("SBC", "11:30", None, 1, 0, 1390),
        ]
    },
    
    # Train 49: MAS-NDLS Rajdhani
    {
        "number": "12433",
        "name": "Chennai Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Wed,Fri",
        "stops": [
            ("MAS", "06:10", "06:10", 0, 0, 0),
            ("RU", "07:50", "07:52", 0, 2, 133),
            ("BZA", "13:50", "14:00", 0, 10, 432),
            ("NGP", "22:40", "22:50", 0, 10, 1067),
            ("BPL", "04:25", "04:35", 1, 10, 1477),
            ("AGC", "11:00", "11:05", 1, 5, 1919),
            ("NZM", "13:15", None, 1, 0, 2182),
        ]
    },
    
    # Train 50: HWH-MAS Mail
    {
        "number": "12839",
        "name": "Howrah-Chennai Mail",
        "type": "MAIL",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HWH", "23:00", "23:00", 0, 0, 0),
            ("KGP", "01:20", "01:25", 1, 5, 113),
            ("BBS", "06:50", "07:00", 1, 10, 440),
            ("VSKP", "12:50", "13:00", 1, 10, 756),
            ("BZA", "18:45", "18:55", 1, 10, 1090),
            ("MAS", "04:00", None, 2, 0, 1663),
        ]
    },

    # Train 51: NDLS-BPL Shatabdi (evening)
    {
        "number": "12002",
        "name": "NDLS-BPL Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("NDLS", "06:15", "06:15", 0, 0, 0),
            ("AGC", "08:08", "08:10", 0, 2, 195),
            ("JHS", "10:30", "10:35", 0, 5, 413),
            ("BPL", "14:30", None, 0, 0, 690),
        ]
    },

    # Train 52: NDLS-LKO Shatabdi
    {
        "number": "12004",
        "name": "NDLS-LKO Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("NDLS", "15:15", "15:15", 0, 0, 0),
            ("CNB", "19:25", "19:27", 0, 2, 440),
            ("LKO", "21:30", None, 0, 0, 512),
        ]
    },

    # Train 53: SBC-PUNE Express
    {
        "number": "12296",
        "name": "SBC-PUNE Duronto Express",
        "type": "DURONTO",
        "runs_on": "Mon,Wed,Fri",
        "stops": [
            ("SBC", "23:00", "23:00", 0, 0, 0),
            ("UBL", "08:30", "08:40", 1, 10, 432),
            ("PUNE", "18:20", None, 1, 0, 880),
        ]
    },

    # Train 54: CBE-MAS Intercity
    {
        "number": "12673",
        "name": "Cheran Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("CBE", "06:00", "06:00", 0, 0, 0),
            ("SA", "08:30", "08:35", 0, 5, 160),
            ("JTJ", "10:40", "10:45", 0, 5, 290),
            ("MAS", "14:00", None, 0, 0, 500),
        ]
    },

    # Train 55: TVC-NDLS Kerala Express
    {
        "number": "12625",
        "name": "Kerala Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("TVC", "11:15", "11:15", 0, 0, 0),
            ("ERS", "15:20", "15:30", 0, 10, 210),
            ("CBE", "22:00", "22:10", 0, 10, 426),
            ("SA", "00:30", "00:35", 1, 5, 586),
            ("JTJ", "02:50", "03:00", 1, 10, 716),
            ("GTL", "07:25", "07:35", 1, 10, 916),
            ("SC", "14:30", "14:45", 1, 15, 1240),
            ("NGP", "00:10", "00:25", 2, 15, 1826),
            ("BPL", "07:50", "08:00", 2, 10, 2236),
            ("JHS", "12:35", "12:40", 2, 5, 2455),
            ("AGC", "15:20", "15:25", 2, 5, 2653),
            ("NDLS", "19:15", None, 2, 0, 3030),
        ]
    },

    # Train 56: NDLS-JP Double Decker
    {
        "number": "12985",
        "name": "NDLS-JP Double Decker Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NDLS", "06:05", "06:05", 0, 0, 0),
            ("JP", "10:35", None, 0, 0, 308),
        ]
    },

    # Train 57: JP-NDLS Double Decker (return)
    {
        "number": "12986",
        "name": "JP-NDLS Double Decker Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("JP", "17:30", "17:30", 0, 0, 0),
            ("NDLS", "22:30", None, 0, 0, 308),
        ]
    },

    # Train 58: MAS-SBC Night Express  
    {
        "number": "12608",
        "name": "MAS-SBC Lalbagh Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("MAS", "22:30", "22:30", 0, 0, 0),
            ("JTJ", "01:25", "01:27", 1, 2, 196),
            ("SBC", "05:30", None, 1, 0, 362),
        ]
    },

    # Train 59: BPL-NGP Intercity
    {
        "number": "12141",
        "name": "BPL-NGP Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("BPL", "14:15", "14:15", 0, 0, 0),
            ("ET", "16:10", "16:15", 0, 5, 95),
            ("NGP", "22:30", None, 0, 0, 410),
        ]
    },

    # Train 60: NGP-BPL Intercity (return)
    {
        "number": "12142",
        "name": "NGP-BPL Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NGP", "06:30", "06:30", 0, 0, 0),
            ("ET", "12:15", "12:20", 0, 5, 315),
            ("BPL", "14:30", None, 0, 0, 410),
        ]
    },

    # ═══════════════════════════════════════════════════════
    # SHORTER FEEDER ROUTES (create more connections)
    # ═══════════════════════════════════════════════════════

    # Train 61: NDLS-AGC Intercity
    {
        "number": "12179",
        "name": "NDLS-AGC Intercity Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NDLS", "07:15", "07:15", 0, 0, 0),
            ("MTJ", "09:05", "09:08", 0, 3, 137),
            ("AGC", "09:45", None, 0, 0, 195),
        ]
    },

    # Train 62: AGC-NDLS Intercity (return)
    {
        "number": "12180",
        "name": "AGC-NDLS Intercity Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("AGC", "17:50", "17:50", 0, 0, 0),
            ("MTJ", "18:30", "18:33", 0, 3, 58),
            ("NDLS", "20:30", None, 0, 0, 195),
        ]
    },

    # Train 63: CDG-NDLS Shatabdi
    {
        "number": "12045",
        "name": "CDG-NDLS Shatabdi Express",
        "type": "SHATABDI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat",
        "stops": [
            ("CDG", "07:40", "07:40", 0, 0, 0),
            ("UMB", "08:10", "08:12", 0, 2, 46),
            ("NDLS", "11:30", None, 0, 0, 253),
        ]
    },

    # Train 64: GHY-NDLS Rajdhani
    {
        "number": "12423",
        "name": "Guwahati Rajdhani Express",
        "type": "RAJDHANI",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("GHY", "15:05", "15:05", 0, 0, 0),
            ("NJP", "21:15", "21:25", 0, 10, 400),
            ("PNBE", "05:50", "06:00", 1, 10, 907),
            ("MGS", "07:20", "07:25", 1, 5, 1015),
            ("CNB", "11:55", "12:00", 1, 5, 1299),
            ("NDLS", "16:15", None, 1, 0, 1898),
        ]
    },

    # Train 65: HWH-PNBE Express
    {
        "number": "13131",
        "name": "HWH-PNBE Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("HWH", "19:15", "19:15", 0, 0, 0),
            ("ASN", "22:35", "22:40", 0, 5, 203),
            ("DHN", "00:10", "00:15", 1, 5, 265),
            ("GY", "04:05", "04:10", 1, 5, 453),
            ("PNBE", "08:30", None, 1, 0, 564),
        ]
    },

    # Train 66: PUNE-SC Express
    {
        "number": "17031",
        "name": "Pune-Hyderabad Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("PUNE", "17:15", "17:15", 0, 0, 0),
            ("SRE", "22:10", "22:20", 0, 10, 264),
            ("WADI", "01:10", "01:20", 1, 10, 408),
            ("GTL", "05:10", "05:20", 1, 10, 526),
            ("SC", "12:30", None, 1, 0, 660),
        ]
    },

    # Train 67: NDLS-HWH via Patna Express
    {
        "number": "12311",
        "name": "NDLS-HWH Kalka Mail",
        "type": "MAIL",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NDLS", "07:40", "07:40", 0, 0, 0),
            ("CNB", "13:00", "13:10", 0, 10, 440),
            ("ALD", "16:00", "16:10", 0, 10, 637),
            ("MGS", "18:30", "18:50", 0, 20, 748),
            ("GY", "20:40", "20:45", 0, 5, 936),
            ("DHN", "01:25", "01:30", 1, 5, 1124),
            ("ASN", "02:45", "02:50", 1, 5, 1186),
            ("BWN", "05:00", "05:05", 1, 5, 1327),
            ("HWH", "07:55", None, 1, 0, 1447),
        ]
    },

    # Train 68: SBC-MYS Express
    {
        "number": "12614",
        "name": "SBC-MYS Tippu Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "15:00", "15:00", 0, 0, 0),
            ("MYS", "18:15", None, 0, 0, 139),
        ]
    },

    # Train 69: BPL-SC Express
    {
        "number": "12791",
        "name": "BPL-SC Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Wed,Fri,Sun",
        "stops": [
            ("BPL", "16:00", "16:00", 0, 0, 0),
            ("ET", "18:10", "18:15", 0, 5, 95),
            ("NGP", "00:30", "00:45", 1, 15, 410),
            ("SC", "10:15", None, 1, 0, 996),
        ]
    },

    # Train 70: SC-BPL Express (return)
    {
        "number": "12792",
        "name": "SC-BPL Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Tue,Thu,Sat",
        "stops": [
            ("SC", "14:30", "14:30", 0, 0, 0),
            ("NGP", "23:20", "23:35", 0, 15, 586),
            ("ET", "06:00", "06:05", 1, 5, 901),
            ("BPL", "08:10", None, 1, 0, 996),
        ]
    },

    # Train 71: KOTA-NGP Express (cross-route)
    {
        "number": "19311",
        "name": "KOTA-NGP Express",
        "type": "EXPRESS",
        "runs_on": "Mon,Thu",
        "stops": [
            ("KOTA", "09:00", "09:00", 0, 0, 0),
            ("BPL", "18:30", "18:45", 0, 15, 350),
            ("ET", "20:50", "20:55", 0, 5, 445),
            ("JBP", "01:00", "01:10", 1, 10, 580),
            ("NGP", "08:30", None, 1, 0, 760),
        ]
    },

    # Train 72: SBC-CBE Intercity
    {
        "number": "12609",
        "name": "SBC-CBE Intercity Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SBC", "06:15", "06:15", 0, 0, 0),
            ("MYS", "09:30", "09:35", 0, 5, 139),
            ("CBE", "15:00", None, 0, 0, 365),
        ]
    },

    # Train 73: NGP-SC Express (night)
    {
        "number": "12749",
        "name": "NGP-SC Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NGP", "21:30", "21:30", 0, 0, 0),
            ("SC", "08:45", None, 1, 0, 586),
        ]
    },

    # Train 74: SC-NGP Express (return)
    {
        "number": "12750",
        "name": "SC-NGP Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("SC", "21:00", "21:00", 0, 0, 0),
            ("NGP", "07:15", None, 1, 0, 586),
        ]
    },

    # Train 75: NDLS-JP Superfast (afternoon)
    {
        "number": "12413",
        "name": "NDLS-JP Superfast Express",
        "type": "SUPERFAST",
        "runs_on": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "stops": [
            ("NDLS", "15:50", "15:50", 0, 0, 0),
            ("JP", "21:00", None, 0, 0, 308),
        ]
    },
]
