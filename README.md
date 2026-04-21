# 🌾 AgriCRM — Agricultural CRM System

## 📁 Project Files
```
agricrm/
├── login.html        ← Login + Register + Forgot Password page
├── dashboard.html    ← Full Dashboard (all features)
├── app.py            ← Python Flask Backend
├── schema.sql        ← MySQL Database Schema
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## 🚀 VS Code Setup (Step by Step)

### STEP 1 — Install Python Libraries
Open terminal in VS Code (`Ctrl + ~`) and run:
```bash
pip install -r requirements.txt
```

### STEP 2 — Setup MySQL Database
1. Open **MySQL Workbench** or **phpMyAdmin**
2. Open the file `schema.sql`
3. Run it (press ▶ or Ctrl+Enter)
4. This creates the database with sample data ✅

### STEP 3 — Configure Database Password
Open `app.py` and find this section (around line 40):
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',        # ← PUT YOUR MYSQL PASSWORD HERE
    'database': 'agricrm',
}
```

### STEP 4 — Run the Backend
In VS Code terminal:
```bash
python app.py
```
You'll see:
```
🌾  AgriCRM Backend Starting...
🌐  URL  : http://localhost:5000
🔑  Login: admin / admin123
```

### STEP 5 — Open in Browser
Go to: **http://localhost:5000**

---

## 🔑 Login Credentials
| Field    | Value       |
|----------|-------------|
| Username | `admin`     |
| Password | `admin123`  |

---

## ✨ All Features

### 🔐 Login Page
- Username & Password login
- Register / Sign Up (new account)
- Forgot Password flow
- Beautiful earthy organic design

### 🏠 Dashboard
- Stats: Farmers count, Temperature, Crop prices, Pending tasks
- Live Weather widget with city search
- Farming advisory based on weather
- Recent farmers table

### 🌤 Weather Info
- Search any city in India/world
- Temperature, Humidity, Wind speed
- Rain prediction
- Pressure readings
- Smart farming advisory (irrigation, pest, field work)

### 👨‍🌾 Farmer Management
- Add farmer (name, contact, location, crops, land size)
- Edit farmer details
- Delete farmer
- Search & filter farmers
- Status tracking (Active/Inactive/New)

### 📊 Market Prices
- Add crop prices (Wheat, Rice, Onion, etc.)
- Price per quintal in ₹
- Market/Mandi name
- Price trend (↑ Rising / ↓ Falling / → Stable)
- Edit & Delete entries

### 📋 Tasks & Reminders
- Fertilizer application reminders
- Irrigation schedules
- Harvest time alerts
- Pest control tasks
- Priority levels (Normal / High / Urgent)
- Mark as Done

### 🔔 Notifications
- Rain expected alerts
- Market price changes
- Harvest reminders
- Fertilizer reminders

### 📝 Activity Log
- Tracks all actions in the system

### ✏️ Profile Page
- Edit name, username, email
- Change password

---

## 🗄️ MySQL Tables
| Table           | Purpose                    |
|-----------------|----------------------------|
| `users`         | Login accounts             |
| `farmers`       | Farmer records             |
| `market_prices` | Crop market prices         |
| `tasks`         | Reminders & tasks          |
| `activity_log`  | System activity history    |

---

## 🌐 API Endpoints
| Method | Endpoint               | Description           |
|--------|------------------------|-----------------------|
| POST   | /api/login             | User login            |
| POST   | /api/register          | New user registration |
| POST   | /api/forgot-password   | Password reset        |
| POST   | /api/profile           | Update profile        |
| GET    | /api/farmers           | Get all farmers       |
| POST   | /api/farmers/add       | Add single farmer     |
| PUT    | /api/farmers/<id>      | Update farmer         |
| DELETE | /api/farmers/<id>      | Delete farmer         |
| GET    | /api/market            | Get market prices     |
| POST   | /api/market/add        | Add price entry       |
| GET    | /api/tasks             | Get all tasks         |
| POST   | /api/tasks/add         | Add task              |
| GET    | /api/stats             | Dashboard stats       |
| GET    | /api/activity          | Activity log          |

---

## 📱 Works Without Backend Too!
If MySQL isn't set up yet, the app still works fully:
- All data is saved in browser **localStorage**
- Open `login.html` directly in browser
- Login with: `admin` / `admin123`

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python 3 + Flask
- **Database**: MySQL
- **Weather**: OpenWeatherMap API (free)
- **Fonts**: Google Fonts (Cormorant Garamond + Outfit)
