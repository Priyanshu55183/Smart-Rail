"""
Seed Data — 120 Indian Railway Stations
========================================
Real stations with accurate coordinates, zones, categories, and
station-specific transfer times.

Why hand-curated?
- Random data would produce nonsensical routes
- Real station positions make map visualization work
- Accurate transfer times make the Dijkstra algorithm realistic
- Station categories affect ML delay prediction features

Corridors covered:
- Delhi ↔ Mumbai (Western corridor)
- Delhi ↔ Kolkata (Eastern corridor)  
- Delhi ↔ Chennai (Central/Southern corridor)
- Mumbai ↔ Chennai (Konkan/Southern)
- Delhi ↔ Bengaluru (via Hyderabad)
- Kolkata ↔ Chennai (Eastern coast)
- Mumbai ↔ Kolkata (via Nagpur)
- Cross routes (Jaipur, Lucknow, Bhopal, etc.)

Transfer time logic:
- A1 stations (New Delhi, Mumbai CST, Howrah): 45 min (huge, crowded)
- A stations (Bengaluru, Secunderabad): 35-40 min
- B junctions (Itarsi, Jolarpettai): 25-30 min  
- C/D stations: 20 min
"""

# Each tuple: (code, name, city, state, zone, category, lat, lon, is_junction, min_transfer, platforms)
STATIONS_DATA = [
    # ── A1 / A Category — Major Metros ────────────────────
    ("NDLS", "New Delhi", "New Delhi", "Delhi", "NR", "A1", 28.6424, 77.2196, True, 45, 16),
    ("DLI", "Old Delhi Junction", "Delhi", "Delhi", "NR", "A", 28.6618, 77.2281, True, 40, 14),
    ("ANVT", "Anand Vihar Terminal", "Delhi", "Delhi", "NR", "A", 28.6468, 77.3152, False, 30, 7),
    ("DEE", "Delhi Sarai Rohilla", "Delhi", "Delhi", "NR", "A", 28.6618, 77.1773, False, 25, 6),
    
    ("BCT", "Mumbai Central", "Mumbai", "Maharashtra", "WR", "A1", 18.9690, 72.8197, True, 45, 10),
    ("CSMT", "Chhatrapati Shivaji Terminus", "Mumbai", "Maharashtra", "CR", "A1", 18.9402, 72.8356, True, 45, 18),
    ("LTT", "Lokmanya Tilak Terminus", "Mumbai", "Maharashtra", "CR", "A", 19.0685, 72.8888, False, 30, 9),
    ("BVI", "Borivali", "Mumbai", "Maharashtra", "WR", "B", 19.2282, 72.8567, False, 20, 8),
    
    ("HWH", "Howrah Junction", "Kolkata", "West Bengal", "ER", "A1", 22.5840, 88.3425, True, 45, 23),
    ("SDAH", "Sealdah", "Kolkata", "West Bengal", "ER", "A1", 22.5647, 88.3739, True, 40, 13),
    ("KOAA", "Kolkata Terminal", "Kolkata", "West Bengal", "ER", "A", 22.5353, 88.3401, False, 30, 5),
    
    ("MAS", "Chennai Central", "Chennai", "Tamil Nadu", "SR", "A1", 13.0822, 80.2753, True, 40, 12),
    ("MS", "Chennai Egmore", "Chennai", "Tamil Nadu", "SR", "A", 13.0768, 80.2622, True, 35, 11),
    
    ("SBC", "KSR Bengaluru City Junction", "Bengaluru", "Karnataka", "SWR", "A1", 12.9773, 77.5706, True, 40, 10),
    ("YPR", "Yesvantpur Junction", "Bengaluru", "Karnataka", "SWR", "A", 13.0195, 77.5340, True, 30, 6),
    
    ("SC", "Secunderabad Junction", "Hyderabad", "Telangana", "SCR", "A1", 17.4339, 78.5009, True, 40, 10),
    ("HYB", "Hyderabad Deccan", "Hyderabad", "Telangana", "SCR", "A", 17.3753, 78.4707, True, 35, 6),
    ("KCG", "Kacheguda", "Hyderabad", "Telangana", "SCR", "A", 17.3595, 78.4786, True, 30, 7),
    
    ("JP", "Jaipur Junction", "Jaipur", "Rajasthan", "NWR", "A", 26.9208, 75.7874, True, 35, 8),
    ("LKO", "Lucknow Charbagh", "Lucknow", "Uttar Pradesh", "NR", "A", 26.8308, 80.9218, True, 35, 9),
    ("PNBE", "Patna Junction", "Patna", "Bihar", "ECR", "A", 25.6072, 85.1366, True, 35, 10),
    ("CNB", "Kanpur Central", "Kanpur", "Uttar Pradesh", "NCR", "A", 26.4446, 80.3509, True, 35, 9),
    ("ALD", "Prayagraj Junction", "Prayagraj", "Uttar Pradesh", "NCR", "A", 25.4335, 81.8462, True, 35, 10),
    ("BSB", "Varanasi Junction", "Varanasi", "Uttar Pradesh", "NR", "A", 25.3150, 83.0168, True, 35, 9),
    ("ADI", "Ahmedabad Junction", "Ahmedabad", "Gujarat", "WR", "A", 23.0270, 72.6003, True, 35, 12),
    
    # ── B Category — Important Junctions ──────────────────
    ("AGC", "Agra Cantt", "Agra", "Uttar Pradesh", "NCR", "B", 27.1539, 78.0099, True, 30, 7),
    ("BPL", "Bhopal Junction", "Bhopal", "Madhya Pradesh", "WCR", "A", 23.2685, 77.4116, True, 35, 6),
    ("NGP", "Nagpur Junction", "Nagpur", "Maharashtra", "CR", "A", 21.1486, 79.0863, True, 35, 8),
    ("BZA", "Vijayawada Junction", "Vijayawada", "Andhra Pradesh", "SCR", "A", 16.5173, 80.6221, True, 35, 10),
    ("GWL", "Gwalior Junction", "Gwalior", "Madhya Pradesh", "NCR", "B", 26.2206, 78.1826, True, 25, 5),
    ("JHS", "Jhansi Junction", "Jhansi", "Uttar Pradesh", "NCR", "B", 25.4426, 78.5579, True, 30, 8),
    ("ET", "Itarsi Junction", "Itarsi", "Madhya Pradesh", "WCR", "B", 22.6137, 77.7629, True, 25, 7),
    ("BRC", "Vadodara Junction", "Vadodara", "Gujarat", "WR", "A", 22.3097, 73.1849, True, 30, 6),
    ("ST", "Surat", "Surat", "Gujarat", "WR", "B", 21.2059, 72.8404, True, 25, 5),
    ("RTM", "Ratlam Junction", "Ratlam", "Madhya Pradesh", "WR", "B", 23.3315, 75.0413, True, 25, 5),
    ("VSKP", "Visakhapatnam Junction", "Visakhapatnam", "Andhra Pradesh", "ECoR", "A", 17.7215, 83.2920, True, 30, 8),
    ("RNC", "Ranchi Junction", "Ranchi", "Jharkhand", "SER", "A", 23.3136, 85.3197, True, 30, 7),
    ("TVC", "Thiruvananthapuram Central", "Thiruvananthapuram", "Kerala", "SR", "A", 8.4893, 76.9526, True, 30, 5),
    ("ERS", "Ernakulam Junction", "Kochi", "Kerala", "SR", "A", 9.9818, 76.2895, True, 30, 5),
    ("CBE", "Coimbatore Junction", "Coimbatore", "Tamil Nadu", "SR", "A", 11.0013, 76.9653, True, 30, 6),
    ("MDU", "Madurai Junction", "Madurai", "Tamil Nadu", "SR", "B", 9.9170, 78.1278, True, 25, 6),
    ("PUNE", "Pune Junction", "Pune", "Maharashtra", "CR", "A", 18.5274, 73.8741, True, 30, 6),
    ("NED", "Nanded", "Nanded", "Maharashtra", "SCR", "B", 19.1614, 77.3233, False, 20, 4),
    ("GNT", "Guntur Junction", "Guntur", "Andhra Pradesh", "SCR", "B", 16.3027, 80.4357, True, 25, 5),
    
    # ── B/C Category — Junctions and Medium Stations ──────
    ("JTJ", "Jolarpettai Junction", "Jolarpettai", "Tamil Nadu", "SR", "B", 12.5764, 78.5736, True, 25, 4),
    ("RU", "Renigunta Junction", "Renigunta", "Andhra Pradesh", "SCR", "B", 13.6346, 79.5121, True, 25, 4),
    ("GTL", "Guntakal Junction", "Guntakal", "Andhra Pradesh", "SCR", "B", 15.1632, 77.3698, True, 25, 6),
    ("DMM", "Dharmavaram Junction", "Dharmavaram", "Andhra Pradesh", "SCR", "B", 14.4146, 77.7214, True, 20, 4),
    ("WADI", "Wadi Junction", "Wadi", "Karnataka", "CR", "B", 17.0511, 76.9829, True, 25, 4),
    ("DD", "Daund Junction", "Daund", "Maharashtra", "CR", "B", 18.4576, 74.5817, True, 25, 4),
    ("KGP", "Kharagpur Junction", "Kharagpur", "West Bengal", "SER", "B", 22.3450, 87.3178, True, 25, 6),
    ("TATA", "Tatanagar Junction", "Jamshedpur", "Jharkhand", "SER", "B", 22.7859, 86.1992, True, 25, 6),
    ("BBS", "Bhubaneswar", "Bhubaneswar", "Odisha", "ECoR", "A", 20.2766, 85.8378, True, 30, 7),
    ("CTC", "Cuttack Junction", "Cuttack", "Odisha", "ECoR", "B", 20.4650, 85.8819, True, 25, 5),
    ("SBP", "Sambalpur Junction", "Sambalpur", "Odisha", "ECoR", "B", 21.4619, 83.9730, True, 20, 5),
    ("R", "Raipur Junction", "Raipur", "Chhattisgarh", "SECR", "A", 21.2331, 81.6317, True, 30, 6),
    ("BPQ", "Balharshah", "Balharshah", "Maharashtra", "CR", "B", 19.8468, 79.3408, True, 25, 4),
    ("BSL", "Bhusaval Junction", "Bhusaval", "Maharashtra", "CR", "B", 21.0363, 75.7749, True, 30, 5),
    ("MMR", "Manmad Junction", "Manmad", "Maharashtra", "CR", "B", 20.2580, 74.4330, True, 25, 4),
    ("AWB", "Aurangabad", "Aurangabad", "Maharashtra", "SCR", "B", 19.8721, 75.3313, False, 20, 3),
    ("UDZ", "Udaipur City", "Udaipur", "Rajasthan", "NWR", "B", 24.5780, 73.6835, False, 20, 4),
    ("AII", "Ajmer Junction", "Ajmer", "Rajasthan", "NWR", "B", 26.4537, 74.6349, True, 25, 5),
    ("JU", "Jodhpur Junction", "Jodhpur", "Rajasthan", "NWR", "B", 26.2875, 73.0178, True, 25, 5),
    ("BKN", "Bikaner Junction", "Bikaner", "Rajasthan", "NWR", "B", 28.0195, 73.3209, False, 20, 5),
    ("DWK", "Dwarka", "Dwarka", "Gujarat", "WR", "C", 22.2385, 68.9724, False, 20, 2),
    ("BDTS", "Bandra Terminus", "Mumbai", "Maharashtra", "WR", "A", 19.0543, 72.8399, False, 30, 9),
    ("CSTM", "Mumbai CSMT", "Mumbai", "Maharashtra", "CR", "A1", 18.9398, 72.8355, True, 45, 18),
    
    # ── C/D Category — Smaller Stations ───────────────────
    ("MTJ", "Mathura Junction", "Mathura", "Uttar Pradesh", "NCR", "B", 27.4704, 77.6723, True, 25, 6),
    ("SRE", "Solapur Junction", "Solapur", "Maharashtra", "CR", "B", 17.6589, 75.9109, True, 25, 5),
    ("GY", "Gaya Junction", "Gaya", "Bihar", "ECR", "B", 24.7953, 84.9890, True, 25, 5),
    ("MGS", "Mughal Sarai Junction", "Chandauli", "Uttar Pradesh", "ECR", "B", 25.2812, 83.1122, True, 30, 8),
    ("DHN", "Dhanbad Junction", "Dhanbad", "Jharkhand", "ECR", "B", 23.7935, 86.4353, True, 25, 6),
    ("ASN", "Asansol Junction", "Asansol", "West Bengal", "ER", "B", 23.6850, 86.9540, True, 25, 6),
    ("BWN", "Barddhaman Junction", "Bardhaman", "West Bengal", "ER", "B", 23.2416, 87.8569, True, 20, 5),
    ("DGR", "Durg Junction", "Durg", "Chhattisgarh", "SECR", "B", 21.2064, 81.2846, True, 20, 4),
    ("KTE", "Katni Junction", "Katni", "Madhya Pradesh", "WCR", "B", 23.8295, 80.3829, True, 25, 5),
    ("JBP", "Jabalpur", "Jabalpur", "Madhya Pradesh", "WCR", "B", 23.1643, 79.9305, True, 25, 5),
    ("HBJ", "Habibganj", "Bhopal", "Madhya Pradesh", "WCR", "A", 23.2296, 77.4371, False, 25, 6),
    ("UJN", "Ujjain Junction", "Ujjain", "Madhya Pradesh", "WR", "B", 23.1711, 75.7800, True, 20, 5),
    ("KNW", "Kanpur Anwarganj", "Kanpur", "Uttar Pradesh", "NR", "C", 26.4544, 80.3288, False, 20, 3),
    ("LJN", "Lucknow Junction", "Lucknow", "Uttar Pradesh", "NER", "A", 26.8600, 80.9449, True, 35, 9),
    ("GKP", "Gorakhpur Junction", "Gorakhpur", "Uttar Pradesh", "NER", "A", 26.7538, 83.3704, True, 30, 10),
    ("MB", "Moradabad Junction", "Moradabad", "Uttar Pradesh", "NR", "B", 28.8373, 78.7673, True, 25, 6),
    ("BE", "Bareilly Junction", "Bareilly", "Uttar Pradesh", "NR", "B", 28.3481, 79.4290, True, 25, 5),
    ("DDN", "Dehradun", "Dehradun", "Uttarakhand", "NR", "B", 30.3174, 78.0321, False, 20, 5),
    ("CDG", "Chandigarh Junction", "Chandigarh", "Chandigarh", "NR", "A", 30.6895, 76.8188, True, 30, 5),
    ("LDH", "Ludhiana Junction", "Ludhiana", "Punjab", "NR", "A", 30.8793, 75.8657, True, 25, 6),
    ("ASR", "Amritsar Junction", "Amritsar", "Punjab", "NR", "A", 31.6351, 74.8680, True, 30, 6),
    ("JAT", "Jammu Tawi", "Jammu", "Jammu & Kashmir", "NR", "A", 32.7293, 74.8629, False, 25, 5),
    ("UMB", "Ambala Cantt Junction", "Ambala", "Haryana", "NR", "B", 30.3668, 76.7963, True, 30, 7),
    ("RE", "Rewa", "Rewa", "Madhya Pradesh", "WCR", "C", 24.5338, 81.2979, False, 20, 3),
    ("KOTA", "Kota Junction", "Kota", "Rajasthan", "WCR", "B", 25.1856, 75.8589, True, 25, 6),
    ("SWM", "Sawai Madhopur Junction", "Sawai Madhopur", "Rajasthan", "WCR", "B", 26.0186, 76.3518, True, 20, 5),
    ("NZM", "Hazrat Nizamuddin", "Delhi", "Delhi", "NR", "A", 28.5888, 77.2509, True, 35, 7),
    ("MYS", "Mysuru Junction", "Mysuru", "Karnataka", "SWR", "B", 12.2999, 76.6552, True, 25, 6),
    ("UBL", "Hubballi Junction", "Hubballi", "Karnataka", "SWR", "B", 15.3374, 75.0957, True, 25, 6),
    ("BJP", "Bijapur", "Bijapur", "Karnataka", "SWR", "C", 16.8270, 75.7224, False, 20, 3),
    ("TPTY", "Tirupati", "Tirupati", "Andhra Pradesh", "SCR", "B", 13.6335, 79.4089, True, 25, 5),
    ("SA", "Salem Junction", "Salem", "Tamil Nadu", "SR", "B", 11.6605, 78.1418, True, 25, 5),
    ("TPJ", "Tiruchirappalli Junction", "Tiruchirappalli", "Tamil Nadu", "SR", "B", 10.7932, 78.6852, True, 25, 6),
    ("MQ", "Mangaluru Central", "Mangaluru", "Karnataka", "SR", "B", 12.8716, 74.8780, False, 25, 4),
    ("MAQ", "Mangaluru Junction", "Mangaluru", "Karnataka", "SWR", "B", 12.8702, 74.8855, True, 25, 4),
    ("GOA", "Goa (Madgaon)", "Madgaon", "Goa", "KR", "B", 15.2843, 74.0023, False, 20, 3),
    ("RJT", "Rajkot Junction", "Rajkot", "Gujarat", "WR", "B", 22.3019, 70.7912, True, 25, 5),
    ("INDB", "Indore Junction", "Indore", "Madhya Pradesh", "WR", "A", 22.7183, 75.8016, True, 30, 6),
    ("GWL", "Gwalior Junction", "Gwalior", "Madhya Pradesh", "NCR", "B", 26.2206, 78.1826, True, 25, 5),
    ("NJP", "New Jalpaiguri Junction", "Siliguri", "West Bengal", "NFR", "A", 26.6972, 88.4310, True, 30, 7),
    ("GHY", "Guwahati", "Guwahati", "Assam", "NFR", "A", 26.1760, 91.7542, True, 30, 8),
    ("DBRG", "Dibrugarh Town", "Dibrugarh", "Assam", "NFR", "B", 27.4823, 94.8940, False, 20, 4),
    ("RMM", "Rameswaram", "Rameswaram", "Tamil Nadu", "SR", "C", 9.2876, 79.3129, False, 20, 2),
    ("KYQ", "Kamakhya Junction", "Guwahati", "Assam", "NFR", "B", 26.1599, 91.7195, True, 25, 5),
    ("BJU", "Barauni Junction", "Barauni", "Bihar", "ECR", "B", 25.4662, 86.1256, True, 20, 5),
    ("SPJ", "Samastipur Junction", "Samastipur", "Bihar", "ECR", "B", 25.8524, 85.7890, True, 20, 5),
    ("MFP", "Muzaffarpur Junction", "Muzaffarpur", "Bihar", "ECR", "B", 26.1202, 85.3960, True, 20, 5),
    ("SEE", "Sonpur Junction", "Sonpur", "Bihar", "ECR", "B", 25.6500, 85.1667, True, 20, 4),
    ("DBG", "Darbhanga Junction", "Darbhanga", "Bihar", "ECR", "B", 26.1558, 85.9102, True, 20, 5),
    ("KIR", "Katihar Junction", "Katihar", "Bihar", "NFR", "B", 25.5393, 87.5660, True, 25, 6),
    ("BGP", "Bhagalpur", "Bhagalpur", "Bihar", "ER", "B", 25.2498, 86.9809, False, 20, 5),
    ("RGD", "Rajgir", "Rajgir", "Bihar", "ECR", "C", 25.0315, 85.4177, False, 15, 2),
    ("JMP", "Jamalpur Junction", "Jamalpur", "Bihar", "ER", "C", 25.3124, 86.4897, True, 20, 4),
    ("GMO", "Gomoh Junction", "Gomoh", "Jharkhand", "ECR", "B", 23.8782, 86.1567, True, 20, 4),
    ("HTE", "Hatia", "Ranchi", "Jharkhand", "SER", "B", 23.3267, 85.2909, False, 20, 4),
    ("CKP", "Chakradharpur", "Chakradharpur", "Jharkhand", "SER", "B", 22.6850, 85.6298, True, 20, 5),
    ("JSG", "Jharsuguda Junction", "Jharsuguda", "Odisha", "SER", "B", 21.8569, 84.0146, True, 20, 5),
    ("ROU", "Rourkela Junction", "Rourkela", "Odisha", "SER", "B", 22.2596, 84.8498, True, 20, 5),
    ("BNW", "Bhawanagar Terminus", "Bhavnagar", "Gujarat", "WR", "C", 21.7744, 72.1511, False, 20, 4),
    ("SVDK", "Shri Mata Vaishno Devi Katra", "Katra", "Jammu & Kashmir", "NR", "B", 32.9910, 74.9318, False, 20, 4),
]
