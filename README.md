# Price Guardian 

> A smart, automated web application built with Flask that tracks online product prices, bypasses anti-bot defenses, predicts price trends using AI, and sends instant email notifications.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) ![Brevo API](https://img.shields.io/badge/Brevo_API-0092FF?style=for-the-badge&logo=sendinblue&logoColor=white)


## Architecture Pipeline

* **1. User Auth & Session Management:** Secure user registration and login using `Flask-Login` with `scrypt` password hashing and SQLite storage.
* **2. Background Monitoring Thread:** A dedicated daemon thread that continuously runs price checks in the background without freezing the web server.
* **3. Stealth Scraping Engine:** Uses `undetected_chromedriver` alongside a dynamically generated Chrome extension to handle authenticated proxies and bypass bot detection.
* **4. AI Price Prediction:** Collects price history records in SQLite and runs them through a custom `price_ai` module to predict future short-term and long-term price drops.
* **5. Email Notifications:** Triggers automatic email alerts via the Brevo (Sendinblue) REST API whenever a product drops below the user's target price.

---

##  Technical Challenges & Solution

The hardest part of building Price Guardian was dealing with anti-bot detection on e-commerce websites. Normal Selenium scripts were blocked almost instantly. On top of that, running Chrome in headless mode made it really tricky to use proxies that require a username and password authentication.

To solve this, I wrote a Python function (`create_proxy_extension`) that generates a custom Manifest V3 Chrome extension on the fly to handle proxy credentials seamlessly. Combined with `undetected_chromedriver`, custom Chrome DevTools Protocol (CDP) scripts to hide `navigator.webdriver`, and randomized User-Agents, the scraper was able to run smoothly in the background without getting flagged or IP-blocked.

---

## Tech Stack

| Category | Technologies & Tools |
| :--- | :--- |
| **Backend & Auth** | Python, Flask, Flask-Login, Werkzeug (`scrypt`), Multi-threading |
| **Scraping & Automation** | `undetected_chromedriver`, Selenium, Custom Chrome Extension (Manifest V3), CDP Scripts |
| **Database & AI** | SQLite3, Custom `price_ai` Module (Time-series Prediction), JSON |
| **APIs & Notifications** | Brevo API (Sendinblue), `requests` |

---

##  Quick Start

### 1. Clone the repository & install dependencies

```bash
git clone [https://github.com/yourusername/price-guardian.git](https://github.com/yourusername/price-guardian.git)
cd price-guardian
pip install -r requirements.txt
```

### 2. Set up environment & run

Set your environment variables and start the Flask application:

```bash
export PORT=10000
python app.py
```

*The app will automatically initialize the database, start the background price-checking thread, and serve the website locally.*
