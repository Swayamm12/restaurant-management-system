# 🍴 Restaurant Management System
### I have used Laragon for MySQL

## 🗂️ PROJECT STRUCTURE

```
restaurant_mgmt/
├── index.html                  ← Login page
├── database/
│   ├── schema.sql              ← CREATE TABLE statements
│   └── sample_data.sql         ← INSERT sample data + VIEWs
├── backend/
│   └── app.py                  ← Flask REST API
└── frontend/
    ├── css/
    │   └── style.css           ← All styles
    ├── js/
    │   └── api.js              ← Shared API helpers
    └── pages/
        ├── dashboard.html      ← KPI stats + active orders
        ├── menu.html           ← Menu CRUD
        ├── orders.html         ← Order creation + tracking
        ├── tables.html         ← Table status management
        ├── customers.html      ← Customer database
        └── reports.html        ← Sales analytics
```

---

## ⚙️ SETUP INSTRUCTIONS

### Step 1 — Install dependencies
```bash
pip install flask flask-mysqldb flask-cors
```

### Step 2 — Set up MySQL database
```bash
mysql -u root -p
```
```sql
source /path/to/restaurant_mgmt/database/schema.sql
source /path/to/restaurant_mgmt/database/sample_data.sql
```

### Step 3 — Configure database connection
Open `backend/app.py` and update:
```python
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
```

### Step 4 — Start the Flask backend
```bash
cd restaurant_mgmt/backend
python app.py
```
Flask runs on: http://localhost:5000

### Step 5 — Open the frontend
Open `restaurant_mgmt/index.html` in your browser.
> Tip: Use VS Code Live Server extension for best results.

### Default Login
- Username: `admin`
- Password: `admin123`

---

## 🗄️ KEY DBMS CONCEPTS DEMONSTRATED

| Concept | Where Used |
|---|---|
| **Normalization (1NF/2NF/3NF)** | Separate tables for categories, customers, items |
| **Primary Keys** | All tables have `AUTO_INCREMENT` PKs |
| **Foreign Keys** | 7 FK relationships with ON DELETE rules |
| **Computed Columns** | `subtotal` in order_items (auto-calculated) |
| **Views** | `v_order_summary`, `v_popular_items`, `v_daily_sales` |
| **Transactions** | Order creation rolls back if any insert fails |
| **Indexes** | On `orders.status`, `orders.created_at`, etc. |
| **Aggregate Functions** | SUM, COUNT, AVG in reports |
| **JOINs** | Multi-table JOINs in orders, reports |
| **ENUM Constraints** | status fields use ENUM for data integrity |
| **CHECK Constraints** | price > 0, quantity > 0 |

---

## 🔌 API ENDPOINTS REFERENCE

### Auth
| Method | URL | Description |
|---|---|---|
| POST | /api/login | Login with username/password |
| POST | /api/logout | End session |
| GET | /api/me | Get current user |

### Menu
| Method | URL | Description |
|---|---|---|
| GET | /api/menu | List all items (with JOIN to categories) |
| POST | /api/menu | Create new item |
| PUT | /api/menu/:id | Update item |
| DELETE | /api/menu/:id | Delete item |

### Orders
| Method | URL | Description |
|---|---|---|
| GET | /api/orders | List all (filterable by ?status=) |
| GET | /api/orders/:id | Full order with items |
| POST | /api/orders | Create order (uses transaction) |
| PUT | /api/orders/:id/status | Update status |
| GET | /api/orders/:id/bill | Calculate bill |

### Payments
| Method | URL | Description |
|---|---|---|
| POST | /api/payments | Process payment + complete order |

### Reports
| Method | URL | Description |
|---|---|---|
| GET | /api/reports/dashboard | KPI stats |
| GET | /api/reports/popular-items | Top selling items |
| GET | /api/reports/sales | Daily sales history |
