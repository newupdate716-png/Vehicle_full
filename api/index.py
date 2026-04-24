from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def clean_text(text):
    if text:
        # অতিরিক্ত স্পেস এবং নিউ-লাইন রিমুভ করে ক্লিন করে
        return " ".join(text.split())
    return "N/A"

def parse_all_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = {}

    # ১. বেসিক হেডার ইনফো
    header_section = soup.find('div', class_='hrc-details-card')
    results['registration_number'] = clean_text(header_section.find('h1').text) if header_section and header_section.find('h1') else "N/A"

    # ডেটা এক্সট্রাকশন হেল্পার (লেবেল অনুযায়ী ভ্যালু খোঁজা)
    def get_data(label):
        # span এর ভেতর লেবেল টেক্সট খুঁজে তার প্যারেন্ট থেকে p ট্যাগ নেওয়া
        target = soup.find('span', string=re.compile(label, re.IGNORECASE))
        if not target:
            # যদি সরাসরি না পায়, তবে লুপ চালিয়ে চেক করা (কিছু ক্ষেত্রে স্পেস থাকে)
            for s in soup.find_all('span'):
                if label.lower() in s.text.lower():
                    target = s
                    break
        
        if target:
            parent = target.find_parent()
            if parent:
                val = parent.find('p')
                return clean_text(val.text) if val else "N/A"
        return "N/A"

    # ২. ওনারশিপ ডিটেইলস (Ownership Details)
    results['ownership_details'] = {
        "owner_name": get_data("Owner Name"),
        "registration_number": get_data("Registration Number"),
        "financier": get_data("Financier Name"),
        "registered_rto": get_data("Registered RTO")
    }

    # ৩. ভেহিকেল ডিটেইলস (Vehicle Details)
    results['vehicle_details'] = {
        "maker_model": get_data("Maker Model"),
        "vehicle_class": get_data("Vehicle Class"),
        "fuel_type": get_data("Fuel Type"),
        "engine_number": "Hidden in Web", # সিকিউরিটি কারণে ওয়েবসাইট হাইড রাখে
        "chassis_number": "Hidden in Web"
    }

    # ৪. ইনস্যুরেন্স ইনফো (Insurance Information)
    insurance_card = soup.find('div', class_='insurance-alert-box')
    results['insurance_details'] = {
        "status": "Active" if insurance_card and 'active' in insurance_card.get('class', []) else "Expired/Inactive",
        "insurance_company": get_data("Insurance Company"),
        "insurance_expiry": get_data("Insurance Expiry"),
        "valid_upto": get_data("Insurance Upto"),
        "policy_number": "Check App for Full Details"
    }

    # ৫. গুরুত্বপূর্ণ তারিখ (Important Dates & Validity)
    results['validity_dates'] = {
        "registration_date": get_data("Registration Date"),
        "vehicle_age": get_data("Vehicle Age"),
        "fitness_upto": get_data("Fitness Upto"),
        "tax_upto": get_data("Tax Upto"),
        "insurance_expiry_countdown": get_data("Insurance Expiry In")
    }

    # ৬. আরটিও কন্টাক্ট (RTO Contact)
    results['rto_info'] = {
        "rto_code": get_data("Code"),
        "city": get_data("City Name"),
        "phone": get_data("Phone"),
        "address": get_data("Address"),
        "website": get_data("Website")
    }

    # ৭. আদার ইনফরমেশন (অন্যান্য তথ্য যা ব্লার থাকে সেগুলো থেকে নাম সংগ্রহ)
    results['additional_info'] = {
        "cubic_capacity": get_data("Cubic Capacity"),
        "seating_capacity": get_data("Seating Capacity"),
        "permit_type": get_data("Permit Type"),
        "blacklist_status": get_data("Blacklist Status"),
        "noc_details": get_data("NOC Details")
    }

    return results

# আপনার রিকোয়েস্ট অনুযায়ী রাউট সেটআপ: /vehicle=PLATE
@app.route('/vehicle=<reg_no>', methods=['GET'])
def get_vehicle(reg_no):
    # সেশন হ্যান্ডলিং (প্রয়োজন হলে কুকি অটোমেটিক ম্যানেজ করবে)
    session = requests.Session()
    url = f"https://vahanx.in/rc-search/{reg_no}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://vahanx.in/rc-search'
    }

    try:
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            final_data = parse_all_data(response.text)
            return jsonify({
                "status": "success",
                "developer": "SB Sakib",
                "results": final_data
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": f"Server returned status {response.status_code}"
            }), response.status_code
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "message": "Premium Vahan RC API is Live",
        "usage": "/vehicle=GJ21DB1119",
        "dev": "SB Sakib"
    })

if __name__ == '__main__':
    app.run(debug=True)