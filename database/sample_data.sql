-- ============================================================
-- RESTAURANT MANAGEMENT SYSTEM - SAMPLE DATA
-- Run this AFTER schema.sql
-- ============================================================



-- ============================================================
-- USERS (admin + staff)
-- Password is 'password123' hashed with MD5 (use bcrypt in real apps!)
-- ============================================================
INSERT INTO users (username, password, full_name, role) VALUES
('admin',    MD5('admin123'),    'SWAYAM.S',   'admin'),
('staff1',   MD5('staff123'),    'Priya Patel',    'staff'),
('staff2',   MD5('staff123'),    'Amit Verma',     'staff');

-- ============================================================
-- CUSTOMERS
-- ============================================================
INSERT INTO customers (full_name, phone, email) VALUES
('Ananya Iyer',      '9876543210', 'ananya@email.com'),
('Rohan Mehta',      '9812345678', 'rohan@email.com'),
('Sneha Kapoor',     '9934567890', NULL),
('Vikram Singh',     '9765432100', 'vikram@email.com'),
('Pooja Nair',       '9823456789', NULL);

-- ============================================================
-- RESTAURANT TABLES
-- ============================================================
INSERT INTO restaurant_tables (table_number, capacity, status) VALUES
(1, 2, 'available'),
(2, 4, 'occupied'),
(3, 4, 'available'),
(4, 6, 'available'),
(5, 6, 'reserved'),
(6, 8, 'available'),
(7, 2, 'occupied'),
(8, 4, 'available');

-- ============================================================
-- CATEGORIES
-- ============================================================
INSERT INTO categories (name, description) VALUES
('Starters',    'Appetizers and snacks'),
('Main Course', 'Full meals and entrees'),
('Breads',      'Roti, Naan, Paratha'),
('Rice & Biryani', 'Rice dishes'),
('Desserts',    'Sweet dishes'),
('Beverages',   'Drinks and juices'),
('Chinese',     'Indo-Chinese dishes');

-- ============================================================
-- MENU ITEMS
-- ============================================================
INSERT INTO menu_items (category_id, name, description, price, is_available) VALUES
-- Starters (category_id=1)
(1, 'Paneer Tikka',       'Grilled cottage cheese with spices',    220.00, TRUE),
(1, 'Chicken 65',         'Spicy deep-fried chicken',              250.00, TRUE),
(1, 'Veg Spring Rolls',   'Crispy vegetable rolls',                150.00, TRUE),
(1, 'Samosa (2 pcs)',     'Fried pastry with potato filling',       60.00, TRUE),

-- Main Course (category_id=2)
(2, 'Butter Chicken',     'Creamy tomato-based chicken curry',     320.00, TRUE),
(2, 'Paneer Butter Masala','Cottage cheese in rich gravy',         280.00, TRUE),
(2, 'Dal Makhani',        'Slow-cooked black lentils',             200.00, TRUE),
(2, 'Mutton Rogan Josh',  'Aromatic lamb curry',                   380.00, TRUE),

-- Breads (category_id=3)
(3, 'Butter Naan',        'Soft leavened bread',                    40.00, TRUE),
(3, 'Garlic Naan',        'Naan with garlic butter',                50.00, TRUE),
(3, 'Tandoori Roti',      'Whole wheat bread from tandoor',         30.00, TRUE),

-- Rice & Biryani (category_id=4)
(4, 'Chicken Biryani',    'Fragrant basmati rice with chicken',    350.00, TRUE),
(4, 'Veg Biryani',        'Basmati rice with mixed vegetables',    250.00, TRUE),
(4, 'Jeera Rice',         'Cumin-flavored steamed rice',           120.00, TRUE),

-- Desserts (category_id=5)
(5, 'Gulab Jamun',        'Soft milk dumplings in sugar syrup',     80.00, TRUE),
(5, 'Kulfi',              'Traditional Indian ice cream',           90.00, TRUE),
(5, 'Rasgulla',           'Spongy cottage cheese balls',            80.00, TRUE),

-- Beverages (category_id=6)
(6, 'Sweet Lassi',        'Chilled yogurt drink',                   80.00, TRUE),
(6, 'Masala Chai',        'Spiced Indian tea',                      40.00, TRUE),
(6, 'Fresh Lime Soda',    'Lime juice with soda',                   60.00, TRUE),

-- Chinese (category_id=7)
(7, 'Veg Fried Rice',     'Stir-fried rice with vegetables',       180.00, TRUE),
(7, 'Chicken Manchurian', 'Chicken in spicy Chinese sauce',        270.00, TRUE);

-- ============================================================
-- ORDERS (sample orders)
-- ============================================================
INSERT INTO orders (customer_id, table_id, user_id, status, notes) VALUES
(1, 2, 2, 'completed', 'No onions please'),
(2, 7, 2, 'preparing', NULL),
(3, 3, 3, 'pending',   'Extra spicy'),
(4, 4, 2, 'served',    NULL),
(5, 1, 3, 'completed', NULL);

-- ============================================================
-- ORDER ITEMS (line items per order)
-- ============================================================
INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES
-- Order 1
(1, 1,  1, 220.00),   -- Paneer Tikka x1
(1, 5,  1, 320.00),   -- Butter Chicken x1
(1, 9,  2, 40.00),    -- Butter Naan x2
(1, 18, 2, 80.00),    -- Sweet Lassi x2
-- Order 2
(2, 2,  1, 250.00),   -- Chicken 65
(2, 12, 1, 350.00),   -- Chicken Biryani
(2, 20, 1, 40.00),    -- Masala Chai
-- Order 3
(3, 6,  1, 280.00),   -- Paneer Butter Masala
(3, 14, 1, 120.00),   -- Jeera Rice
(3, 11, 2, 30.00),    -- Tandoori Roti x2
-- Order 4
(4, 8,  1, 380.00),   -- Mutton Rogan Josh
(4, 10, 2, 50.00),    -- Garlic Naan x2
(4, 19, 1, 40.00),    -- Masala Chai
-- Order 5
(5, 22, 1, 270.00),   -- Chicken Manchurian
(5, 21, 1, 180.00),   -- Veg Fried Rice
(5, 20, 1, 60.00);    -- Fresh Lime Soda

-- ============================================================
-- PAYMENTS
-- ============================================================
INSERT INTO payments (order_id, total_amount, tax_amount, discount, final_amount, payment_method, payment_status, paid_at)
VALUES
(1, 780.00,  46.80,  0.00,  826.80, 'card', 'paid',    NOW()),
(4, 520.00,  31.20,  0.00,  551.20, 'cash', 'paid',    NOW()),
(5, 510.00,  30.60, 50.00,  490.60, 'upi',  'paid',    NOW());

-- ============================================================
-- USEFUL VIEWS (like virtual tables - important DBMS concept)
-- ============================================================

-- View: Order summary with customer and table details
CREATE OR REPLACE VIEW v_order_summary AS
SELECT
    o.order_id,
    o.created_at          AS order_date,
    COALESCE(c.full_name, 'Walk-in') AS customer_name,
    c.phone,
    rt.table_number,
    u.full_name           AS staff_name,
    o.status,
    SUM(oi.subtotal)      AS order_total
FROM orders o
LEFT JOIN customers c           ON o.customer_id = c.customer_id
JOIN restaurant_tables rt       ON o.table_id = rt.table_id
JOIN users u                    ON o.user_id = u.user_id
JOIN order_items oi             ON o.order_id = oi.order_id
GROUP BY o.order_id, o.created_at, customer_name, c.phone, rt.table_number, u.full_name, o.status;

-- View: Popular items report
CREATE OR REPLACE VIEW v_popular_items AS
SELECT
    mi.name                     AS item_name,
    cat.name                    AS category,
    mi.price,
    SUM(oi.quantity)            AS total_ordered,
    SUM(oi.subtotal)            AS total_revenue
FROM order_items oi
JOIN menu_items mi  ON oi.item_id = mi.item_id
JOIN categories cat ON mi.category_id = cat.category_id
GROUP BY mi.item_id, mi.name, cat.name, mi.price
ORDER BY total_ordered DESC;

-- View: Daily sales report
CREATE OR REPLACE VIEW v_daily_sales AS
SELECT
    DATE(p.paid_at)             AS sale_date,
    COUNT(p.payment_id)         AS total_orders,
    SUM(p.total_amount)         AS gross_sales,
    SUM(p.tax_amount)           AS tax_collected,
    SUM(p.discount)             AS discounts_given,
    SUM(p.final_amount)         AS net_revenue
FROM payments p
WHERE p.payment_status = 'paid'
GROUP BY DATE(p.paid_at)
ORDER BY sale_date DESC;