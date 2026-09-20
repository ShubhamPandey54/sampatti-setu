DELHI_PS = [
    {"code": "PS-CP", "name": "Connaught Place", "district": "New Delhi"},
    {"code": "PS-KB", "name": "Karol Bagh", "district": "Central Delhi"},
    {"code": "PS-CH", "name": "Chandni Chowk", "district": "North Delhi"},
    {"code": "PS-HK", "name": "Hauz Khas", "district": "South Delhi"},
    {"code": "PS-SK", "name": "Saket", "district": "South Delhi"},
    {"code": "PS-LN", "name": "Lajpat Nagar", "district": "South East Delhi"},
    {"code": "PS-DW", "name": "Dwarka Sector 9", "district": "South West Delhi"},
    {"code": "PS-VK", "name": "Vasant Kunj", "district": "South West Delhi"},
    {"code": "PS-RH", "name": "Rohini Sector 3", "district": "North West Delhi"},
    {"code": "PS-JP", "name": "Janakpuri", "district": "West Delhi"},
    {"code": "PS-PV", "name": "Preet Vihar", "district": "East Delhi"},
    {"code": "PS-MN", "name": "Mayur Vihar", "district": "East Delhi"},
    {"code": "PS-SD", "name": "Shahdara", "district": "Shahdara"},
    {"code": "PS-NJ", "name": "Najafgarh", "district": "South West Delhi"},
]

PS_TO_DISTRICT = {p["code"]: p["district"] for p in DELHI_PS}

CATEGORIES = [
    "Mobile Phone", "Laptop / Tablet", "Wallet / Purse",
    "Documents (Aadhaar/PAN/Passport)", "Jewellery", "Two-Wheeler",
    "Bicycle", "Bag / Backpack", "Watch", "Other Electronics", "Other",
]

FOUND_STAGES = [
    "Reported by Citizen",
    "Verified by Duty Officer",
    "Entered in Malkhana Register",
    "Under Matching Review",
    "Claim Verification (Owner Identified)",
    "Returned to Owner",
]

FIR_STAGES = [
    "Complaint Filed",
    "Registered at Police Station",
    "Under Investigation",
    "Possible Match Found",
    "Ownership Verification",
    "Item Recovered & Closed",
]
