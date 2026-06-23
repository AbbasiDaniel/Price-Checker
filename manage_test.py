from flask import Flask, request, render_template
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
import requests 
app = Flask(__name__)
Api_Key="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"
CHROMEDRIVER_PATH = r"C:\Users\Daniel\Desktop\chromedriver144\chromedriver-win64\chromedriver.exe"
SELENIUM_PROFILE = r"C:\Users\Daniel\Desktop\selenium_profile"

def get_all_trackers():
    Connection = sqlite3.connect("trackers.db")
    Connection.row_factory = sqlite3.Row  
    Edit = Connection.cursor()
    #print("alllaaaahhh")
    Edit.execute("SELECT * FROM trackers")
    rows = Edit.fetchall()
    Connection.close()
    return rows

def get_driver():
    #print("hello")
    options = uc.ChromeOptions()
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
    driver = uc.Chrome(options=options, version_main=148)
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

#########################################################
def get_price_from_walmart(url):
    price = get_price_with_selenium(url, wait_seconds=15)
    #print("**********")
    #print(price)
    if price is not None:
        print("Price found via Selenium:", price, flush=True)
    return price

def init_db():
    #check_prices()
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
            notified BOOLEAN DEFAULT 0
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

def check_prices():
    Connection = sqlite3.connect("trackers.db")
    Edit = Connection.cursor()
    Edit.execute("SELECT id, email, product_url, target_price FROM trackers WHERE notified = 0")
    List = Edit.fetchall()
    print("price checker function")
    for row in List:
        tracker_id, email, product_url, target_price = row
        print("walmarting...")
        current_price = get_price_from_walmart(product_url)
        Edit.execute("UPDATE trackers SET current_price = ? WHERE id = ?", (current_price,tracker_id,))
        Connection.commit()
        if current_price != None:
            #current_price=1000000000000000
            if current_price <= target_price:
                print("111111111")
                send_email(email, product_url, current_price)
                Edit.execute("UPDATE trackers SET notified = 1 WHERE id = ?", (tracker_id,))
                Connection.commit()
                
    Connection.close()

def send_email(email, product_url, current_price):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {Api_Key}",
        "Content-Type": "application/json"
    }
    data = {
        "personalizations": [{
            "to": [{"email": email}],
            "subject": "Your product is now cheaper"
        }],
        "from": {"email": "pricechecker.alert@outlook.com"},
        "content": [{
            "type": "text/plain",
            "value": f"Your product: {product_url} is now cheaper at {current_price}"
        }]
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 202:
        print("Success")
    else:
        print("Error", response.status_code, response.text)

def background_checker():
    interval_hours = 6
    while True:
        #print("checking")
        check_prices()
        #print("bekhab")
        time.sleep(interval_hours * 3600)

@app.route("/", methods=["GET", "POST"])
def index():
    price = None
    trackers = get_all_trackers()
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
            add_tracker(1,email,product_url,current_price,TargetPrice)
        return redirect(url_for('index'))
        
    return render_template("form - Copy.html", price=price,trackers=trackers)


if __name__ == "__main__":
    init_db()
    #print("working woooowwww")
    thread = threading.Thread(target=background_checker)
    thread.daemon = True
    thread.start()

    app.run(debug=True,use_reloader=False)
