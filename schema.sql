-- ╔══════════════════════════════════════════════════╗
-- ║       AgriCRM — MySQL Database Schema           ║
-- ╚══════════════════════════════════════════════════╝
-- Run this file in MySQL Workbench or phpMyAdmin

CREATE DATABASE IF NOT EXISTS agricrm
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE agricrm;

-- ─────────────────────────────────────
-- USERS TABLE
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    username    VARCHAR(50)         NOT NULL UNIQUE,
    email       VARCHAR(150)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,   -- SHA-256 hash
    is_active   TINYINT(1)          DEFAULT 1,
    last_login  DATETIME            NULL,
    created_at  DATETIME            DEFAULT CURRENT_TIMESTAMP
);

-- Default admin user (password: admin123)
INSERT INTO users (name, username, email, password, created_at)
VALUES (
  'Admin User',
  'admin',
  'admin@agri.com',
  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a',  -- SHA-256 of 'admin123'
  NOW()
) ON DUPLICATE KEY UPDATE id=id;


-- ─────────────────────────────────────
-- FARMERS TABLE
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS farmers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20)     NULL,
    location        VARCHAR(200)    NULL,
    land_size       DECIMAL(10,2)   NULL COMMENT 'in acres',
    primary_crop    VARCHAR(100)    NULL,
    other_crops     VARCHAR(300)    NULL,
    status          ENUM('Active','Inactive','New') DEFAULT 'Active',
    notes           TEXT            NULL,
    joined_date     DATE            NULL,
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        ON UPDATE CURRENT_TIMESTAMP
);

-- Sample farmers
INSERT INTO farmers (name, phone, location, land_size, primary_crop, status) VALUES
('Rajesh Patil',   '9876543210', 'Nashik, Maharashtra',   8.5,  'Grapes',    'Active'),
('Suresh Kumar',   '9823456789', 'Amritsar, Punjab',      12.0, 'Wheat',     'Active'),
('Meena Devi',     '9712345678', 'Patna, Bihar',           5.0, 'Rice',      'Active'),
('Anand Sharma',   '9654321098', 'Jaipur, Rajasthan',      7.0, 'Bajra',     'New'),
('Priya Nair',     '9543210987', 'Thrissur, Kerala',       3.5, 'Coconut',   'Active');


-- ─────────────────────────────────────
-- MARKET PRICES TABLE
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS market_prices (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    crop_name           VARCHAR(100)    NOT NULL,
    price_per_quintal   DECIMAL(10,2)   NOT NULL,
    market_name         VARCHAR(200)    NULL,
    price_date          DATE            NULL,
    trend               VARCHAR(30)     DEFAULT '→ Stable',
    grade               VARCHAR(20)     DEFAULT 'A Grade',
    created_at          DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        ON UPDATE CURRENT_TIMESTAMP
);

-- Sample prices
INSERT INTO market_prices (crop_name, price_per_quintal, market_name, price_date, trend) VALUES
('Wheat',       2150.00, 'Amritsar APMC',    CURDATE(), '↑ Rising'),
('Rice',        2800.00, 'Patna Mandi',      CURDATE(), '→ Stable'),
('Maize',       1850.00, 'Pune APMC',        CURDATE(), '↓ Falling'),
('Soybean',     4200.00, 'Indore Mandi',     CURDATE(), '↑ Rising'),
('Onion',        950.00, 'Nashik APMC',      CURDATE(), '↓ Falling'),
('Tomato',       600.00, 'Pune APMC',        CURDATE(), '↑ Rising'),
('Cotton',      6500.00, 'Nagpur Mandi',     CURDATE(), '→ Stable'),
('Sugarcane',    350.00, 'Kolhapur APMC',    CURDATE(), '→ Stable');


-- ─────────────────────────────────────
-- TASKS / REMINDERS TABLE
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(300)    NOT NULL,
    task_type       VARCHAR(100)    NULL,
    priority        ENUM('Normal','High','Urgent') DEFAULT 'Normal',
    farmer_name     VARCHAR(100)    NULL,
    due_date        DATE            NULL,
    notes           TEXT            NULL,
    status          ENUM('Pending','Done','Cancelled') DEFAULT 'Pending',
    completed_at    DATETIME        NULL,
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- Sample tasks
INSERT INTO tasks (title, task_type, priority, farmer_name, due_date, status) VALUES
('Fertilizer application — NPK',     '💊 Fertilizer', 'Urgent', 'Rajesh Patil',  DATE_ADD(CURDATE(), INTERVAL 2 DAY),  'Pending'),
('Irrigation check — wheat fields',  '💧 Irrigation', 'Normal', 'Suresh Kumar',  DATE_ADD(CURDATE(), INTERVAL 3 DAY),  'Pending'),
('Harvest — Rice crop ready',        '🌾 Harvest',    'High',   'Meena Devi',    DATE_ADD(CURDATE(), INTERVAL 5 DAY),  'Pending'),
('Pest control — aphids detected',   '🐛 Pest Control','Urgent','Anand Sharma',  CURDATE(),                            'Pending'),
('Follow-up call — loan query',      '📞 Follow-up',  'Normal', 'Priya Nair',    DATE_ADD(CURDATE(), INTERVAL 7 DAY),  'Pending');


-- ─────────────────────────────────────
-- ACTIVITY LOG TABLE
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT             NULL,
    action      VARCHAR(100)    NOT NULL,
    detail      TEXT            NULL,
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
);

-- ─────────────────────────────────────
-- VERIFY
-- ─────────────────────────────────────
SELECT 'Database setup complete! ✅' AS status;
SELECT 'Users:'   AS tbl, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Farmers', COUNT(*) FROM farmers
UNION ALL
SELECT 'Prices',  COUNT(*) FROM market_prices
UNION ALL
SELECT 'Tasks',   COUNT(*) FROM tasks;
