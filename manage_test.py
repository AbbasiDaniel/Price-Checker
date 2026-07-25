from flask import Flask, request, render_template, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, re, threading, sqlite3 , random , math , os
from selenium.webdriver.common.action_chains import ActionChains 
from flask import redirect, url_for
import requests, json 
import price_ai
import random
app = Flask(__name__, template_folder='.')
#Api_Key="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"
Api_Key="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"
CHROMEDRIVER_PATH = r"C:\Users\Daniel\Desktop\chromedriver144\chromedriver-win64\chromedriver.exe"
SELENIUM_PROFILE = r"C:\Users\Daniel\Desktop\selenium_profile"

app.secret_key = 'javidshahjavidshahjavidshah'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("trackers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        return User(id=str(user_row[0]), username=user_row[1])
    return None

def get_all_trackers(user_id):
    Connection = sqlite3.connect("trackers.db")
    Connection.row_factory = sqlite3.Row  
    Edit = Connection.cursor()
    #print("alllaaaahhh")
    Edit.execute("SELECT * FROM trackers WHERE user_id = ?", (user_id,))
    rows = Edit.fetchall()
    Connection.close()
    return rows

def get_driver():
    options = uc.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/148.0.7559.60 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.7499.193 Safari/537.36",
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    driver = uc.Chrome(options=options, version_main=150)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """
    })
    return driver

def get_price_with_selenium(url, wait_seconds=120):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(10)
        spans = driver.find_elements(By.CSS_SELECTOR, "span.ux-textspans")
        for span in spans:
            print(2)
            text = span.text.strip()
            print(text)
            num=""
            if text.startswith("$") or text.startswith("U"):
                for c in text:
                    num = "".join(c for c in text if c.isdigit() or c == ".")
                return float(num)
        return None
    finally:
        driver.quit()

def get_price_from_walmart(url):
    price = get_price_with_selenium(url, wait_seconds=15)
    if price is not None:
        print("Price found via Selenium:", price, flush=True)
    return price

def init_db():
    Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("""
        CREATE TABLE IF NOT EXISTS trackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            product_url TEXT NOT NULL,
            current_price REAL,     
            target_price REAL NOT NULL,
            notified BOOLEAN DEFAULT 0,
            price_history TEXT,
            predicted_price_short TEXT,
            predicted_price_long TEXT
        
        )
    """)
    Edit.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    Connection.commit()
    Connection.close()

def add_tracker(user_id, email, product_url,current_price, target_price):
    Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("""
        INSERT INTO trackers (user_id,email, product_url,current_price, target_price, notified)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (user_id, email, product_url,current_price,target_price))
    Connection.commit()
    Connection.close()



def update_predicition(tracker_id, Connection, email, product_url, target_price):
    #Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("SELECT price_history FROM trackers WHERE id = ?", (tracker_id,))
    row = Edit.fetchone()
    if row and row[0]:
        price_list = json.loads(row[0])
    else:
        price_list = []
    if len(price_list)>=10:
        predicted_price=price_ai.predict_price(price_list[len(price_list)-10 : len(price_list)])
        counter=0
        #for price in predicted_price :
            #counter=counter+1
            #if(price <= target_price):
                #send_email_update(email, product_url, price, counter)
                #break
        predicted_price_short=json.dumps(predicted_price[:10])
        predicted_price_long=json.dumps(predicted_price[10:])
        Edit.execute("""
        UPDATE trackers 
        SET predicted_price_short = ?, predicted_price_long = ? 
        WHERE id = ?
        """, (predicted_price_short, predicted_price_long, tracker_id))
    
    Connection.commit()
    #Connection.close()
    return None
 
def update_history(current_price, tracker_id, Connection):

    #Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("SELECT price_history FROM trackers WHERE id = ?", (tracker_id,))
    row = Edit.fetchone()
    if row and row[0]:
        price_list = json.loads(row[0])
    else:
        price_list = []
    price_list.append(current_price)
    price_list=json.dumps(price_list)
    Edit.execute("UPDATE trackers SET price_history = ? WHERE id = ?", (price_list,tracker_id,))
    Connection.commit()
    #Connection.close()
    return None


def check_prices():
    Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("SELECT id, email, product_url, target_price FROM trackers WHERE notified = 0")
    List = Edit.fetchall()
    for row in List:
        tracker_id, email, product_url, target_price = row
        current_price = get_price_from_walmart(product_url)
        #############
        Edit.execute("UPDATE trackers SET current_price = ? WHERE id = ?", (current_price,tracker_id,))
        print("chetori gigar tala?")
        update_history(current_price, tracker_id, Connection)
        update_predicition(tracker_id, Connection, email, product_url, target_price)
        ###########
        Connection.commit()
        if current_price != None:
            if current_price <= target_price:
                send_email(email, product_url, current_price)
                Edit.execute("UPDATE trackers SET notified = 1 WHERE id = ?", (tracker_id,))
                Connection.commit()
                
    Connection.close()

import requests

def send_email(email, product_url, current_price):
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": Api_Key
    }
    
    data = {
        "sender": {
            "name": "Price Notifier",
            "email": "pricechecker.alert@outlook.com"
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Your product is now cheaper",
        "textContent": f"Your product: {product_url} is now cheaper at {current_price}"
    }
    
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Success")
    else:
        print("Error", response.status_code, response.text)

def send_email_update(email, product_url, current_price, hour):
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": Api_Key
    }
    
    data = {
        "sender": {
            "name": "Price Notifier",
            "email": "pricechecker.alert@outlook.com"
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Your product might get cheaper",
        "textContent": f"Your product: {product_url} might get cheaper at {current_price} by {hour} hours"
    }
    
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Success")
    else:
        print("Error", response.status_code, response.text)
def background_checker():
    #cambia este
    interval_hours = 1
    while True:
        print("checking")
        #try:
        check_prices()
        #except Exception:
            #pass
        #finally:
            #print("bekhab")
        time.sleep(interval_hours * 300 + random.randint(0, 900))


def extract_prediction(tracker_id):
    Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("SELECT predicted_price FROM trackers WHERE id = ?", (tracker_id,))
    row = Edit.fetchone()
    predictions=json.loads(row)
    Connection.close()
    return predictions

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    price = None
    trackers = get_all_trackers(current_user.id)
    #price_prediction=extract_prediction() 
    if request.method == "POST":
        product_url = request.form.get("ProductUrl")
        email = request.form.get("Email")
        TargetPrice=request.form.get("TargetPrice")
        if product_url and email and TargetPrice:
            TargetPrice = float(TargetPrice)
            print("adding...")
            try:
                current_price = get_price_from_walmart(product_url)
            except :
                current_price = None
            add_tracker(current_user.id,email,product_url,current_price,TargetPrice)
        return redirect(url_for('index'))
       
    return render_template("form.html", price=price,trackers=trackers)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect("trackers.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row and check_password_hash(user_row[2], password):
            user_obj = User(id=str(user_row[0]), username=user_row[1])
            login_user(user_obj) 
            return redirect(url_for('index')) 
        else:
                return """
                <script>
                    alert("Username or email is incorrect");
                    window.history.back();
                </script>
                """
            
    return render_template('login.html') 

@app.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        re_password=request.form.get('confirm-password')
        if(re_password!=password):
                return """
                <script>
                    alert("Password does not match with the confirm-password");
                    window.history.back();
                </script>
                """
        
        hashed_password = generate_password_hash(password, method='scrypt')
        
        try:
           
            conn = sqlite3.connect("trackers.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
                          return """
                <script>
                    alert("Username already taken, try another one :).");
                    window.history.back();
                </script>
                """
    return render_template('register.html')

if __name__ == "__main__":
    init_db()
    #print("working woooowwww")
    thread = threading.Thread(target=background_checker)
    thread.daemon = True
    thread.start()

    app.run(debug=True,use_reloader=False)
