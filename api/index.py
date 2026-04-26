from flask import Flask, request, jsonify
import requests
import re
import time
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

API_KEY = "TVB_FULL_52F4672E"
API_URL = "https://techvishalboss.com/api/v1/lookup.php"

def get_vehicle_from_vahanx(rc):
    try:
        url = f"https://vahanx.in/rc-search/{rc}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://vahanx.in/rc-search"
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        def get_value(label):
            try:
                div = soup.find("span", string=label)
                if div:
                    parent = div.find_parent("div")
                    if parent:
                        p = parent.find("p")
                        if p:
                            return p.get_text(strip=True)
            except:
                pass
            return ""

        return {
            "owner_name_vx": get_value("Owner Name"),
            "father_name_vx": get_value("Father's Name"),
            "maker_model_vx": get_value("Maker Model"),
            "model_name_vx": get_value("Model Name"),
            "fuel_type_vx": get_value("Fuel Type"),
            "fuel_norms_vx": get_value("Fuel Norms"),
            "reg_date_vx": get_value("Registration Date"),
            "vehicle_class_vx": get_value("Vehicle Class"),
            "registered_rto_vx": get_value("Registered RTO"),
            "address_vx": get_value("Address"),
            "city_vx": get_value("City Name"),
            "insurance_company_vx": get_value("Insurance Company"),
            "insurance_no_vx": get_value("Insurance No"),
            "insurance_upto_vx": get_value("Insurance Upto") or get_value("Insurance Expiry"),
            "fitness_upto_vx": get_value("Fitness Upto"),
            "tax_upto_vx": get_value("Tax Upto"),
            "financier_vx": get_value("Financier Name"),
            "phone_vx": get_value("Phone"),
            "owner_serial_vx": get_value("Owner Serial No"),
            "puc_no_vx": get_value("PUC No"),
            "puc_upto_vx": get_value("PUC Upto")
        }
    except:
        return {}

def get_vehicle_from_tvb(rc):
    try:
        params = {"key": API_KEY, "service": "vehicle", "rc": rc}
        resp = requests.get(API_URL, params=params, timeout=15)
        data = resp.json()
        if data.get("status") and data.get("data", {}).get("response"):
            r = data["data"]["response"]
            rt = r.get("rtoData", {})
            return {
                "rto_name": rt.get("rtoName", ""),
                "rto_code": rt.get("rtoCode", ""),
                "state_name": rt.get("statename", ""),
                "reg_authority": r.get("regAuthority", ""),
                "chassis": r.get("chassis", ""),
                "engine": r.get("engine", ""),
                "reg_date": r.get("regDate", ""),
                "manufacturer": r.get("manufacturer", ""),
                "vehicle_model": r.get("vehicle", ""),
                "vehicle_type": r.get("vehicleType", ""),
                "variant": r.get("variant", ""),
                "fuel_type": r.get("fuelType", ""),
                "cubic_capacity": r.get("cubicCapacity", ""),
                "seat_capacity": r.get("seatCapacity", ""),
                "is_commercial": r.get("isCommercial", False),
                "owner_name": r.get("owner", ""),
                "father_name": r.get("ownerFatherName", ""),
                "financier": r.get("financerName", ""),
                "insurance_company": r.get("insuranceCompanyName", ""),
                "insurance_policy": r.get("insurancePolicyNumber", ""),
                "insurance_upto": r.get("insuranceUpto", ""),
                "insurance_expired": r.get("insuranceExpired", False),
                "present_address": r.get("presentAddress", ""),
                "perm_address": r.get("permAddress", ""),
                "pincode": r.get("pincode", ""),
                "vehicle_class": r.get("vehicleClass", ""),
                "pucc_number": r.get("puccNumber", ""),
                "pucc_upto": r.get("puccValidUpto", "")
            }
    except:
        pass
    return {}

def get_mobile_9step(rc, last5):
    session = requests.Session()
    BASE = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }

    HP = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml?statecd=Mzc2MzM2MzAzNjY0MzIzODM3NjIzNjY0MzY2MjM3NDQ0Yw=="
    HB = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml"
    LI = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/usermgmt/login.xhtml"
    FR = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/balanceservice/form_reschedule_fitness.xhtml"

    for attempt in range(2):
        try:
            r = session.get(HP, headers=BASE, timeout=25)
            vs = re.search(r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', r.text)
            if not vs: continue
            vs = vs.group(1)

            cid = "j_idt193"
            cm = re.search(r'<div[^>]*id="(j_idt\d+)"[^>]*class="[^"]*ui-chkbox', r.text)
            if cm: cid = cm.group(1)

            AH = {
                "Accept": "application/xml, text/xml, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded",
                "Faces-Request": "partial/ajax",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://vahan.parivahan.gov.in",
                "Referer": HP
            }

            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true", "javax.faces.source": "fit_c_office_to",
                "javax.faces.partial.execute": "fit_c_office_to", "javax.faces.behavior.event": "change",
                "homepageformid": "homepageformid", "fit_c_office_to_input": "1", "javax.faces.ViewState": vs
            }, timeout=25)
            m = re.search(r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>', r.text)
            if m: vs = m.group(1)

            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true", "javax.faces.source": cid,
                "javax.faces.partial.execute": cid, "javax.faces.partial.render": "proccedHomeButtonId",
                "javax.faces.behavior.event": "change", "homepageformid": "homepageformid",
                f"{cid}_input": "on", "javax.faces.ViewState": vs
            }, timeout=25)
            m = re.search(r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>', r.text)
            if m: vs = m.group(1)

            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true", "javax.faces.source": "proccedHomeButtonId",
                "javax.faces.partial.execute": "@all", "proccedHomeButtonId": "proccedHomeButtonId",
                "homepageformid": "homepageformid", f"{cid}_input": "on", "javax.faces.ViewState": vs
            }, timeout=25)
            m = re.search(r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>', r.text)
            if m: vs = m.group(1)

            dlg = "j_idt536"
            dm = re.search(r'id="(j_idt\d+)"[^>]*class="[^"]*ui-button', r.text)
            if dm: dlg = dm.group(1)
            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true", "javax.faces.source": dlg,
                "javax.faces.partial.execute": "@all", dlg: dlg, "homepageformid": "homepageformid",
                f"{cid}_input": "on", "javax.faces.ViewState": vs
            }, timeout=25)
            m = re.search(r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>', r.text)
            if m: vs = m.group(1)

            r = session.get(LI + "?faces-redirect=true", headers={**BASE, "Referer": HP}, timeout=25)
            vs = re.search(r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', r.text)
            if not vs: continue
            vs = vs.group(1)

            fit = "j_idt506"
            fm = re.search(r'id="(j_idt\d+)"[^>]*type="submit"', r.text)
            if fm: fit = fm.group(1)
            session.post(LI, headers={**BASE, "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://vahan.parivahan.gov.in", "Referer": LI + "?faces-redirect=true"}, data={
                "loginForm": "loginForm", fit: fit, "javax.faces.ViewState": vs,
                "fitbalcTest": "fitbalcTest", "pur_cd": "86"
            }, timeout=25)

            r = session.get(FR, headers={**BASE, "Referer": LI + "?faces-redirect=true"}, timeout=25)
            vs = re.search(r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', r.text)
            if not vs: continue
            vs = vs.group(1)

            r = session.post(FR, headers={**AH, "Referer": FR}, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "balanceFeesFine:validate_dtls",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "balanceFeesFine:auth_panel",
                "balanceFeesFine:validate_dtls": "balanceFeesFine:validate_dtls",
                "balanceFeesFine": "balanceFeesFine",
                "balanceFeesFine:tf_reg_no": rc,
                "balanceFeesFine:tf_chasis_no": last5,
                "javax.faces.ViewState": vs
            }, timeout=25)

            for p in [r'id="balanceFeesFine:tf_mobile"[^>]*value="(\d{10})"',
                       r'value="(\d{10})"[^>]*id="balanceFeesFine:tf_mobile"',
                       r'tf_mobile[^>]*value="(\d{10})"']:
                m = re.search(p, r.text)
                if m and m.group(1)[0] in "6789":
                    return m.group(1)

            nums = re.findall(r'\b[6-9]\d{9}\b', r.text)
            if nums:
                return nums[0]
        except:
            pass
        if attempt == 0:
            time.sleep(2)
    return None

@app.route("/api/rc", methods=["GET"])
def lookup_vehicle():
    rc = request.args.get("rc", "").strip().upper()
    rc = re.sub(r'[^A-Z0-9]', '', rc)

    if not rc:
        return jsonify({"success": False, "error": "RC parameter required"}), 400

    vx = get_vehicle_from_vahanx(rc)
    tvb = get_vehicle_from_tvb(rc)

    if not vx and not tvb:
        return jsonify({"success": False, "error": "Vehicle not found"}), 404

    chassis = tvb.get("chassis", "").replace(" ", "")
    engine = tvb.get("engine", "")
    last5 = chassis[-5:] if len(chassis) >= 5 else ""

    mobile = None
    if last5:
        mobile = get_mobile_9step(rc, last5)

    result = {
        "success": True,
        "reg_no": rc,
        "owner_name": tvb.get("owner_name") or vx.get("owner_name_vx", ""),
        "father_name": tvb.get("father_name") or vx.get("father_name_vx", ""),
        "maker_model": vx.get("maker_model_vx", ""),
        "manufacturer": tvb.get("manufacturer", ""),
        "model": tvb.get("vehicle_model") or vx.get("model_name_vx", ""),
        "variant": tvb.get("variant", ""),
        "vehicle_type": tvb.get("vehicle_type", ""),
        "vehicle_class": tvb.get("vehicle_class") or vx.get("vehicle_class_vx", ""),
        "fuel_type": tvb.get("fuel_type") or vx.get("fuel_type_vx", ""),
        "fuel_norms": vx.get("fuel_norms_vx", ""),
        "cubic_capacity": tvb.get("cubic_capacity", ""),
        "seat_capacity": tvb.get("seat_capacity", ""),
        "is_commercial": tvb.get("is_commercial", False),
        "reg_date": tvb.get("reg_date") or vx.get("reg_date_vx", ""),
        "rto": tvb.get("reg_authority") or vx.get("registered_rto_vx", ""),
        "rto_code": tvb.get("rto_code", ""),
        "rto_name": tvb.get("rto_name", ""),
        "state": tvb.get("state_name", ""),
        "present_address": tvb.get("present_address") or vx.get("address_vx", ""),
        "permanent_address": tvb.get("perm_address", ""),
        "city": vx.get("city_vx", ""),
        "pincode": tvb.get("pincode", ""),
        "chassis_no": chassis,
        "engine_no": engine,
        "insurance_company": tvb.get("insurance_company") or vx.get("insurance_company_vx", ""),
        "insurance_policy": tvb.get("insurance_policy") or vx.get("insurance_no_vx", ""),
        "insurance_upto": tvb.get("insurance_upto") or vx.get("insurance_upto_vx", ""),
        "insurance_expired": tvb.get("insurance_expired", False),
        "fitness_upto": vx.get("fitness_upto_vx", ""),
        "tax_upto": vx.get("tax_upto_vx", ""),
        "financier": tvb.get("financier") or vx.get("financier_vx", ""),
        "owner_serial": vx.get("owner_serial_vx", ""),
        "pucc_number": tvb.get("pucc_number") or vx.get("puc_no_vx", ""),
        "pucc_upto": tvb.get("pucc_upto") or vx.get("puc_upto_vx", ""),
        "phone": vx.get("phone_vx", ""),
        "mobile": mobile or "Not Available"
    }

    return jsonify(result)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "api": "Vehicle RC Lookup with Mobile",
        "usage": "/api/rc?rc=KA01AB1234"
    })

if __name__ == '__main__':
    app.run(debug=True)