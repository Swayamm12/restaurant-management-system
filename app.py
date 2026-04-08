from flask import Flask, request, jsonify, session
import pymysql.cursors  
from flask_cors import CORS
from datetime import datetime
import hashlib
import os

app = Flask(__name__)


CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

app.secret_key = os.getenv('SECRET_KEY', 'rms_secret_key_dev')

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',             
        password='',             
        database='restaurant_db', 
        port=3306,               
        cursorclass=pymysql.cursors.DictCursor
    )


app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True
)




app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '') 
app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'test_e_db')








def hash_password(password):
    return password

def login_required(f):
    """Decorator to protect routes - checks session"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized. Please login.'}), 401
        return f(*args, **kwargs)
    return decorated





@app.route('/api/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({
            'user_id': session['user_id'],
            'username': session['username'],
            'role': session['role']
        }), 200
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        username = data.get('username')
        
        raw_password = data.get('password', '')
        password = hash_password(raw_password)

        
        conn = get_db_connection()
        cur = conn.cursor()

        
        cur.execute(
            "SELECT user_id, full_name, role FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            
            
            user_data = {
                'user_id': user[0] if isinstance(user, tuple) else user['user_id'],
                'full_name': user[1] if isinstance(user, tuple) else user['full_name'],
                'role': user[2] if isinstance(user, tuple) else user['role']
            }

            
            session['user_id'] = user_data['user_id']
            session['username'] = username
            session['role'] = user_data['role']
            
            
            session.permanent = True 

            return jsonify({'message': 'Login successful', 'user': user_data}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"Login Error: {str(e)}") 
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """POST /api/logout - Clear session"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    """GET /api/me - Get logged-in user info"""
    return jsonify({
        'user_id':  session['user_id'],
        'username': session['username'],
        'role':     session['role']
    })






@app.route('/api/menu', methods=['GET'])
def get_menu():
    """
    GET /api/menu
    Returns all menu items joined with their category name
    Demonstrates: SQL JOIN
    """
    cur = get_db_connection().cursor()
    cur.execute("""
        SELECT mi.item_id, mi.name, mi.description, mi.price, mi.is_available,
               cat.name AS category_name, cat.category_id
        FROM menu_items mi
        JOIN categories cat ON mi.category_id = cat.category_id
        ORDER BY cat.name, mi.name
    """)
    items = cur.fetchall()
    cur.close()
    return jsonify(items)


@app.route('/api/menu', methods=['POST'])
@login_required
def add_menu_item():
    """
    POST /api/menu
    Body: { name, description, price, category_id }
    """
    data = request.get_json()
    
    
    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        cur.execute(
            "INSERT INTO menu_items (category_id, name, description, price) VALUES (%s, %s, %s, %s)",
            (data['category_id'], data['name'], data.get('description', ''), data['price'])
        )
        
        
        db.commit()
        
        new_id = cur.lastrowid
        return jsonify({'message': 'Menu item added', 'item_id': new_id}), 201
        
    except Exception as e:
        
        db.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        
        cur.close()
        db.close()


@app.route('/api/menu/<int:item_id>', methods=['PUT'])
@login_required
def update_menu_item(item_id):
    """
    PUT /api/menu/:id
    Body: { name, description, price, category_id, is_available }
    """
    data = request.get_json()
    
    
    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        cur.execute(
            """UPDATE menu_items 
               SET name=%s, description=%s, price=%s, category_id=%s, is_available=%s 
               WHERE item_id=%s""",
            (data['name'], data.get('description',''), data['price'], 
             data['category_id'], data.get('is_available', True), item_id)
        )
        
        
        db.commit()
        
        return jsonify({'message': 'Menu item updated'})
        
    except Exception as e:
        
        db.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        
        cur.close()
        db.close()

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
@login_required
def delete_menu_item(item_id):
    """
    DELETE /api/menu/:id
    DELETE operation - will fail if item is in an order (FK constraint)
    """
    
    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        cur.execute("DELETE FROM menu_items WHERE item_id=%s", (item_id,))
        
        
        db.commit()
        
        return jsonify({'message': 'Menu item deleted'})
        
    except Exception as e:
        
        db.rollback()
        return jsonify({'error': 'Cannot delete - item exists in orders'}), 400
        
    finally:
        
        db.close()


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """GET /api/categories - For dropdown menus"""
    cur = get_db_connection().cursor()
    cur.execute("SELECT * FROM categories ORDER BY name")
    cats = cur.fetchall()
    cur.close()
    return jsonify(cats)






@app.route('/api/tables', methods=['GET'])
def get_tables():
    """GET /api/tables - All restaurant tables with status"""
    cur = get_db_connection().cursor()
    cur.execute("SELECT * FROM restaurant_tables ORDER BY table_number")
    tables = cur.fetchall()
    cur.close()
    return jsonify(tables)


@app.route('/api/tables/<int:table_id>/status', methods=['PUT'])
@login_required
def update_table_status(table_id):
    """
    PUT /api/tables/:id/status
    Body: { status: 'available' | 'occupied' | 'reserved' }
    """
    data = request.get_json()
    
    
    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        cur.execute(
            "UPDATE restaurant_tables SET status=%s WHERE table_id=%s",
            (data['status'], table_id)
        )
        
        
        db.commit()
        
        return jsonify({'message': 'Table status updated'})
        
    except Exception as e:
        
        db.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        
        cur.close()
        db.close()






@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    """GET /api/customers - All customers, searchable by phone"""
    phone = request.args.get('phone', '')
    cur = get_db_connection().cursor()
    if phone:
        cur.execute("SELECT * FROM customers WHERE phone LIKE %s", (f'%{phone}%',))
    else:
        cur.execute("SELECT * FROM customers ORDER BY full_name")
    customers = cur.fetchall()
    cur.close()
    return jsonify(customers)


@app.route('/api/customers', methods=['POST'])
@login_required
def add_customer():
    """
    POST /api/customers
    Creates a new customer entry. 
    """
    data = request.json
    
    if not data.get('full_name') or not data.get('phone'):
        return jsonify({"error": "Full name and phone are required"}), 400

    
    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        cur.execute("""
            INSERT INTO customers (full_name, phone, email) 
            VALUES (%s, %s, %s)
        """, (data['full_name'], data['phone'], data.get('email', '')))
        
        
        db.commit()
        
        new_id = cur.lastrowid 
        return jsonify({
            "customer_id": new_id, 
            "message": "Customer added successfully"
        }), 201
        
    except Exception as e:
        
        db.rollback()
        print(f"Database Error: {e}")
        return jsonify({"error": "Could not add customer. Phone might already exist."}), 500
        
    finally:
        
        cur.close()
        db.close()





@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    status = request.args.get('status', '')
    cur = get_db_connection().cursor()

    query = """
        SELECT o.order_id, o.created_at, o.status, o.notes,
               COALESCE(o.customer_name, c.full_name, 'Walk-in') AS customer_name,
               COALESCE(c.phone, '') AS phone,
               rt.table_number,
               u.full_name AS staff_name,
               SUM(oi.subtotal) AS order_total
        FROM orders o
        LEFT JOIN customers c           ON o.customer_id = c.customer_id
        JOIN restaurant_tables rt       ON o.table_id = rt.table_id
        JOIN users u                    ON o.user_id = u.user_id
        LEFT JOIN order_items oi         ON o.order_id = oi.order_id
    """
    
    if status:
        query += " WHERE o.status = %s"
        cur.execute(query + " GROUP BY o.order_id ORDER BY o.created_at DESC", (status,))
    else:
        cur.execute(query + " GROUP BY o.order_id ORDER BY o.created_at DESC")

    orders = cur.fetchall()
    cur.close()

    for order in orders:
        if order.get('created_at') and hasattr(order['created_at'], 'strftime'):
            order['created_at'] = order['created_at'].strftime("%d %b %Y, %I:%M %p")
        else:
            order['created_at'] = "Date Not Set"
            
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    try:
        
        db = get_db_connection()
        cur = db.cursor()
        
        
        cur.execute("""
            SELECT o.*, 
                   COALESCE(o.customer_name, c.full_name, 'Walk-in') as customer_name, 
                   c.phone, rt.table_number, u.full_name as staff_name 
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            JOIN restaurant_tables rt ON o.table_id = rt.table_id
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            cur.close()
            db.close()
            return jsonify({"error": "Order not found"}), 404

        
        cur.execute("""
            SELECT oi.*, mi.name as item_name 
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()

        
        cur.execute("SELECT payment_id FROM payments WHERE order_id = %s", (order_id,))
        payment = cur.fetchone()

        
        order_data = dict(order)
        order_data['items'] = [dict(i) for i in items]
        order_data['is_paid'] = True if payment else False

        cur.close()
        db.close()
        return jsonify(order_data)
        
    except Exception as e:
        print(f"Error in get_order_detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """
    POST /api/orders
    Creates an order and multiple line items atomically.
    """
    data = request.get_json()
    items = data.get('items', [])
    
    
    phone = data.get('phone')
    customer_name = data.get('customer_name')
    email = data.get('email', '')
    customer_id = data.get('customer_id')

    if not items:
        return jsonify({'error': 'Order must have at least one item'}), 400

    db = get_db_connection()
    try:
        cur = db.cursor()
        
        
        if not customer_id and phone:
            
            cur.execute("SELECT customer_id FROM customers WHERE phone = %s", (phone,))
            existing = cur.fetchone()
            
            if existing:
                customer_id = existing['customer_id']
            else:
                
                cur.execute(
                    "INSERT INTO customers (full_name, phone, email) VALUES (%s, %s, %s)",
                    (customer_name or 'Walk-in', phone, email)
                )
                customer_id = cur.lastrowid

        
        cur.execute(
            "INSERT INTO orders (customer_id, table_id, user_id, notes, customer_name) VALUES (%s, %s, %s, %s, %s)",
            (
                customer_id, 
                data['table_id'], 
                session['user_id'], 
                data.get('notes',''),
                customer_name 
            )
        )
        order_id = cur.lastrowid

        
        for item in items:
            cur.execute("SELECT price FROM menu_items WHERE item_id=%s", (item['item_id'],))
            menu_item = cur.fetchone()
            if not menu_item:
                raise Exception(f"Item {item['item_id']} not found")

            cur.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                (order_id, item['item_id'], item['quantity'], menu_item['price'])
            )

        
        cur.execute("UPDATE restaurant_tables SET status='occupied' WHERE table_id=%s", (data['table_id'],))

        
        db.commit()
        
        return jsonify({'message': 'Order created', 'order_id': order_id}), 201

    except Exception as e:
        db.rollback() 
        return jsonify({'error': str(e)}), 500
        
    finally:
        cur.close()
        db.close()

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    
    db = get_db_connection()
    try:
        cur = db.cursor()

        
        
        cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        current_record = cur.fetchone()
        
        if not current_record:
            return jsonify({'error': 'Order not found'}), 404
            
        current_status = current_record['status']

        
        if current_status in ['completed', 'cancelled']:
            return jsonify({'error': f'Order is already {current_status} and cannot be changed.'}), 400

        
        cur.execute("UPDATE orders SET status=%s WHERE order_id=%s", (new_status, order_id))

        
        if new_status in ['completed', 'cancelled']:
            cur.execute("SELECT table_id FROM orders WHERE order_id = %s", (order_id,))
            result = cur.fetchone()
            if result and result['table_id']:
                cur.execute("UPDATE restaurant_tables SET status='available' WHERE table_id=%s", (result['table_id'],))

        db.commit()
        return jsonify({'message': f'Order marked as {new_status}'})

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        db.close()





@app.route('/api/orders/<int:order_id>/bill', methods=['GET'])
@login_required
def generate_bill(order_id):
    """
    GET /api/orders/:id/bill
    Calculate the bill for an order (uses computed subtotals)
    Demonstrates: Aggregate functions (SUM, COUNT)
    """
    cur = get_db_connection().cursor()

    cur.execute("""
        SELECT SUM(oi.subtotal) AS subtotal
        FROM order_items oi
        WHERE oi.order_id = %s
    """, (order_id,))
    result = cur.fetchone()
    cur.close()

    subtotal = float(result['subtotal'] or 0)
    tax_rate  = 0.06           
    tax       = round(subtotal * tax_rate, 2)
    total     = round(subtotal + tax, 2)

    return jsonify({
        'order_id': order_id,
        'subtotal': subtotal,
        'tax':      tax,
        'total':    total
    })


@app.route('/api/payments', methods=['POST'])
@login_required
def process_payment():
    """
    POST /api/payments
    Body: { order_id, payment_method, discount }
    Finalize payment and mark order/table as completed
    """
    data = request.get_json()
    order_id = data['order_id']

    
    db = get_db_connection()
    try:
        cur = db.cursor()

        
        cur.execute("SELECT SUM(unit_price * quantity) AS subtotal FROM order_items WHERE order_id=%s", (order_id,))
        result = cur.fetchone()
        
        subtotal = float(result['subtotal'] or 0)
        tax = round(subtotal * 0.06, 2)
        discount = float(data.get('discount', 0))
        final = round(subtotal + tax - discount, 2)

        
        cur.execute("""
            INSERT INTO payments (order_id, total_amount, tax_amount, discount, final_amount, 
                                  payment_method, payment_status, paid_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'paid', NOW())
        """, (order_id, subtotal, tax, discount, final, data.get('payment_method','cash')))

        
        cur.execute("UPDATE orders SET status='completed' WHERE order_id=%s", (order_id,))

        
        cur.execute("""
            UPDATE restaurant_tables SET status='available' 
            WHERE table_id = (SELECT table_id FROM orders WHERE order_id=%s)
        """, (order_id,))

        
        db.commit()
        
        return jsonify({'message': 'Payment processed', 'final_amount': final}), 201

    except Exception as e:
        
        db.rollback()
        print(f"Payment Error: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        
        cur.close()
        db.close()





@app.route('/api/reports/dashboard', methods=['GET'])
@login_required
def dashboard_stats():
    """
    GET /api/reports/dashboard
    Aggregated stats for the dashboard
    Demonstrates: GROUP BY, aggregate functions, subqueries
    """
    cur = get_db_connection().cursor()

    
    cur.execute("""
        SELECT COALESCE(SUM(final_amount), 0) AS today_revenue
        FROM payments
        WHERE DATE(paid_at) = CURDATE() AND payment_status='paid'
    """)
    today = cur.fetchone()

    
    cur.execute("SELECT COUNT(*) AS active_orders FROM orders WHERE status IN ('pending','preparing','served')")
    active = cur.fetchone()

    
    cur.execute("SELECT COUNT(*) AS available FROM restaurant_tables WHERE status='available'")
    tables = cur.fetchone()

    
    cur.execute("SELECT COUNT(*) AS total_orders FROM orders WHERE DATE(created_at) = CURDATE() AND status != 'cancelled'")
    orders_today = cur.fetchone()

    cur.close()
    return jsonify({
        'today_revenue':  float(today['today_revenue']),
        'active_orders':  active['active_orders'],
        'available_tables': tables['available'],
        'orders_today':   orders_today['total_orders']
    })


@app.route('/api/reports/popular-items', methods=['GET'])
@login_required
def popular_items():
    """GET /api/reports/popular-items - Top selling items"""
    cur = get_db_connection().cursor()
    cur.execute("SELECT * FROM v_popular_items LIMIT 10")
    items = cur.fetchall()
    cur.close()
    return jsonify(items)


@app.route('/api/reports/sales', methods=['GET'])
@login_required
def sales_report():
    """GET /api/reports/sales - Daily sales report"""
    cur = get_db_connection().cursor()
    cur.execute("SELECT * FROM v_daily_sales LIMIT 30")
    sales = cur.fetchall()
    cur.close()
    return jsonify(sales)





if __name__ == '__main__':
    
    app.run(debug=True, port=5000)
