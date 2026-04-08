-- ============================================================
-- RESTAURANT MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Course: DBMS Semester 4 Project
-- Concepts: Normalization, Primary Keys, Foreign Keys, Constraints
-- ============================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS restaurant_db;

-- ============================================================
-- TABLE 1: users
-- Stores admin/staff login credentials
-- ============================================================
CREATE TABLE users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,          -- Store hashed password in real apps
    full_name   VARCHAR(100) NOT NULL,
    role        ENUM('admin', 'staff') DEFAULT 'staff',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: customers
-- Stores customer information (normalized - no redundancy)
-- ============================================================
CREATE TABLE customers (
    customer_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    phone         VARCHAR(15) NOT NULL UNIQUE,
    email         VARCHAR(100),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 3: restaurant_tables
-- Tracks physical tables in the restaurant
-- ============================================================
CREATE TABLE restaurant_tables (
    table_id      INT AUTO_INCREMENT PRIMARY KEY,
    table_number  INT NOT NULL UNIQUE,
    capacity      INT NOT NULL DEFAULT 4,
    status        ENUM('available', 'occupied', 'reserved') DEFAULT 'available'
);

-- ============================================================
-- TABLE 4: categories
-- Menu item categories (Starters, Main Course, Drinks, etc.)
-- Separate table = 2NF / 3NF normalization
-- ============================================================
CREATE TABLE categories (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(50) NOT NULL UNIQUE,
    description   VARCHAR(200)
);

-- ============================================================
-- TABLE 5: menu_items
-- Stores all menu items with price and availability
-- FK: category_id references categories(category_id)
-- ============================================================
CREATE TABLE menu_items (
    item_id       INT AUTO_INCREMENT PRIMARY KEY,
    category_id   INT NOT NULL,
    name          VARCHAR(100) NOT NULL,
    description   VARCHAR(300),
    price         DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    is_available  BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- FOREIGN KEY: Links item to a category
    CONSTRAINT fk_menu_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- TABLE 6: orders
-- Master order record - one row per order
-- FK: customer_id, table_id, user_id (who took the order)
-- ============================================================
CREATE TABLE orders (
    order_id      INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT,                          -- NULL = walk-in without registration
    table_id      INT NOT NULL,
    user_id       INT NOT NULL,                 -- Staff who created the order
    status        ENUM('pending', 'preparing', 'served', 'completed', 'cancelled') DEFAULT 'pending',
    notes         VARCHAR(300),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_order_table
        FOREIGN KEY (table_id) REFERENCES restaurant_tables(table_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_order_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- TABLE 7: order_items
-- Line items for each order (Junction/Bridge table)
-- Demonstrates Many-to-Many between orders and menu_items
-- ============================================================
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT NOT NULL,
    item_id       INT NOT NULL,
    quantity      INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price    DECIMAL(10, 2) NOT NULL,      -- Snapshot price at time of order
    subtotal      DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,

    CONSTRAINT fk_oi_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_oi_item
        FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- TABLE 8: payments
-- One payment per completed order
-- FK: order_id references orders(order_id)
-- ============================================================
CREATE TABLE payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL UNIQUE,         -- One payment per order
    total_amount    DECIMAL(10, 2) NOT NULL,
    tax_amount      DECIMAL(10, 2) DEFAULT 0.00,
    discount        DECIMAL(10, 2) DEFAULT 0.00,
    final_amount    DECIMAL(10, 2) NOT NULL,
    payment_method  ENUM('cash', 'card', 'upi') DEFAULT 'cash',
    payment_status  ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    paid_at         TIMESTAMP,

    CONSTRAINT fk_payment_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
-- INDEXES for performance (important DBMS concept)
-- ============================================================
CREATE INDEX idx_orders_status   ON orders(status);
CREATE INDEX idx_orders_date     ON orders(created_at);
CREATE INDEX idx_menu_category   ON menu_items(category_id);
CREATE INDEX idx_oi_order        ON order_items(order_id);
