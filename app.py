from flask import Flask,jsonify,render_template, request, redirect, url_for, jsonify,flash, session ,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from config import Config
from dotenv import load_dotenv
from utils.helpers import sqft_to_m2, w_to_kw, compute_efficiency_pct, predict_expected_output
from utils.geocode import geocode_place
from pathlib import Path
from utils.nasa_api import get_nasa_data
import calendar
import requests
import math
import os

load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
SECRET = os.getenv("FLASK_SECRET", "devsecret123")


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session to work
app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)

# ---------------- Models ---------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 409

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"email": user.email} for user in users]
    return jsonify(user_list)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Email not found'}), 404

    send_reset_email(user.email)
    return jsonify({'message': 'Password reset email sent'}), 200
@app.route('/reset-password-page')
def reset_password_page():
    return render_template('reset_password.html')

# ---------------- Utility ---------------- #

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_reset_email(email):
    token = s.dumps(email, salt='password-reset-salt')
    reset_link = f'http://localhost:5000/reset-password/{token}'
    
    try:
        print(f"Attempting to send email to: {email}")
        msg = Message('Password Reset Request',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Click the link to reset your password: {reset_link}'
        mail.send(msg)
        print("✅ Email sent successfully")
    except Exception as e:
        print("❌ Error sending email:", e)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception as e:
        return "The password reset link is invalid or has expired."

    return render_template('new_password.html', token=token)

@app.route('/reset-password/submit/<token>', methods=['POST'])
def submit_new_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return jsonify({'error': 'Invalid or expired token'}), 400

    data = request.get_json()
    new_password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': 'Password reset successful'}), 200
    return jsonify({'error': 'User not found'}), 404

analysis_result = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/page3")
def page3():
    return render_template("page3.html")

@app.route("/page4")
def page4():
    if not analysis_result:
        return redirect(url_for("page3"))

    return render_template("page4.html", result=analysis_result)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        district = data.get("district")
        lat = data.get("latitude")
        lon = data.get("longitude")

        if not all([district, lat, lon]):
            return jsonify({"error": "Invalid input data"}), 400

        # Call NASA API using utils
        nasa_data = get_nasa_data(lat, lon)

        if not nasa_data:
            return jsonify({"error": "Failed to fetch data from NASA API"}), 500

        ghi = nasa_data["ghi"]
        temp = nasa_data["temperature"]
        sunlight_hours = nasa_data["sunlight_hours"]

        recommendation = "Suitable for Solar Panels ✅" if ghi >= 4.5 else "Not Suitable ❌"

        global analysis_result
        analysis_result = {
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "ghi": ghi,
            "temperature": temp,
            "sunlight_hours": sunlight_hours,
            "recommendation": recommendation
        }

        return redirect(url_for("page4"))

    except Exception as e:
        print("❌ Error in /analyze:", e)
        return jsonify({"error": "Server error occurred"}), 500

@app.route('/geocode')
def geocode():
    query = request.args.get('q')
    api_key = os.getenv('OPENCAGE_API_KEY')
    url = f'https://api.opencagedata.com/geocode/v1/json?q={query}&key={api_key}'
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/page4')
def result_page():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    district = request.args.get('district')

    if not lat or not lng:
        return render_template("page4.html", result=None)

    try:
        lat = float(lat)
        lng = float(lng)
        result = get_nasa_data(lat, lng)  # function from nasa_api.py
        result["district"] = district
    except Exception as e:
        print("NASA API fetch error:", e)
        result = None

    return render_template("page4.html", result=result)

@app.route('/installation', methods=['GET', 'POST'])
def installation():
    result = None
    rooftop_area = " "
    ground_area = " "

    if request.method == 'POST':
        try:
            rooftop_area = request.form['rooftop_area']
            ground_area = request.form['ground_area']

            rooftop = float(rooftop_area)
            ground = float(ground_area)
            rooftop_capacity = rooftop / 100
            ground_capacity = ground / 100

            if rooftop_capacity > ground_capacity:
                result = f"✅ Best to install on *Rooftop*. (Can support approx {rooftop_capacity:.1f} kW system)"
            elif ground_capacity > rooftop_capacity:
                result = f"✅ Best to install on *Ground*. (Can support approx {ground_capacity:.1f} kW system)"
            else:
                result = f"✅ Both Rooftop and Ground can support the same system (~{rooftop_capacity:.1f} kW). Either is suitable."

        except ValueError:
            result = "❌ Please enter valid numbers."

    return render_template('page5.html', result=result,rooftop_area=rooftop_area,ground_area=ground_area)

@app.route('/page5')
def page5():
    return render_template('page5.html')

# Temporary storage to pass values to Page 

# hold last results
page7_results = {}

@app.route("/")
def home():
    return redirect(url_for("page6"))

@app.route("/page6", methods=["GET", "POST"])
def page6():
    global page7_results
    if request.method == "POST":
        try:
            # Read form values
            panel_output_raw = request.form.get("panel_output", "").strip()
            unit = request.form.get("unit", "W").strip()
            panel_area_sqft_raw = request.form.get("panel_area", "").strip()
            energy_consumption_raw = request.form.get("energy_consumption", "").strip()
            location_raw = request.form.get("location", "").strip()

            # Validate required fields
            if not panel_output_raw or not panel_area_sqft_raw or not energy_consumption_raw:
                flash("Please fill panel output, area, and energy consumption.")
                return redirect(url_for("page6"))

            if not location_raw:
                flash("Please enter a location to fetch sunlight data globally.")
                return redirect(url_for("page6"))

            panel_output_val = float(panel_output_raw)   # user input (W or kW depending on unit)
            panel_area_sqft = float(panel_area_sqft_raw)
            energy_consumption_kwh = float(energy_consumption_raw)  # user should enter kWh/day

            # Convert panel output to W if user gave kW
            if unit.lower() == "kw":
                panel_output_w = panel_output_val * 1000.0
            else:
                panel_output_w = panel_output_val

            # Convert area
            panel_area_m2 = sqft_to_m2(panel_area_sqft)
            if panel_area_m2 <= 0:
                flash("Panel area must be positive.")
                return redirect(url_for("page6"))

            # Geocode location
            if not OPENCAGE_API_KEY:
                flash("OpenCage API key not set in .env.")
                return redirect(url_for("page6"))

            coords = geocode_place(location_raw, OPENCAGE_API_KEY)
            if coords is None:
                flash("Could not geocode the location. Try a more specific name.")
                return redirect(url_for("page6"))

            lat, lon = coords

            # NASA data
            nasa = get_nasa_data(lat, lon)
            if not nasa:
                flash("Failed to fetch NASA data for the chosen location.")
                return redirect(url_for("page6"))

            sunlight_hours = float(nasa["sunlight_hours"])
            ghi = float(nasa["ghi"])

            # Efficiency formula
            efficiency_pct = compute_efficiency_pct(panel_output_w, panel_area_m2)

            # Panel power in kW for energy formula
            panel_kw = panel_output_w / 1000.0

            # Predict expected_kwh/day
            expected_kwh = predict_expected_output(panel_kw, sunlight_hours, efficiency_pct)

            if expected_kwh <= 0:
                flash("Predicted expected output is zero or negative. Check inputs.")
                return redirect(url_for("page6"))

            num_panels = energy_consumption_kwh / expected_kwh

            page7_results = {
                "num_panels": math.ceil(num_panels),
                "efficiency": round(efficiency_pct, 2),
                "expected_output": round(expected_kwh, 4),
                "sunlight_hours": round(sunlight_hours, 3),
                "ghi": round(ghi, 3),
                "location": f"{location_raw} ({lat:.4f}, {lon:.4f})"
            }

            return redirect(url_for("page7"))

        except ValueError:
            flash("Please enter valid numeric values.")
            return redirect(url_for("page6"))
        except Exception as e:
            print("Server error:", e)
            flash("Server error occurred.")
            return redirect(url_for("page6"))

    return render_template("page6.html")



@app.route("/page7")
def page7():
    return render_template("page7.html", results=page7_results)

@app.route("/page8", methods=["GET", "POST"])  # Monthly
def monthly_consumption():
    result = None
    if request.method == "POST":
        try:
            usage = float(request.form["usage"])
            month = request.form["month"]
            year = int(request.form["year"])

            # Convert month name to month number
            month_num = list(calendar.month_name).index(month)

            # Get correct number of days in month (leap year safe)
            days = calendar.monthrange(year, month_num)[1]

            # Energy consumption per day
            result = usage / days
        except Exception as e:
            result = f"Error: {e}"

    return render_template("page8.html", result=result)

@app.route("/page9", methods=["GET", "POST"])  # Annual
def annual_consumption():
    result = None
    if request.method == "POST":
        try:
            usage = float(request.form["usage"])
            year = int(request.form["year"])

            # Check leap year
            days = 366 if calendar.isleap(year) else 365

            result = usage / days
        except Exception as e:
            result = f"Error: {e}"

    return render_template("page9.html", result=result)

# ---------------- Run Server ---------------- #
if __name__ == '__main__':
    if not os.path.exists('database/users.db'):
        with app.app_context():
          db.create_all()
    app.run(debug=True)