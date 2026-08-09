CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    loyalty_tier_id INTEGER,
    lifetime_spend REAL NOT NULL,
    FOREIGN KEY (loyalty_tier_id) REFERENCES loyalty_tiers(id)
);
CREATE TABLE IF NOT EXISTS loyalty_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    priority_backorder BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT,
    price REAL,
    vendor_name TEXT,
    vendor_lead_time_days INTEGER,
    inventory_quantity INTEGER
);

INSERT INTO loyalty_tiers VALUES (1, "PLATINUM", true);
INSERT INTO loyalty_tiers VALUES (2, "GOLD", true);
INSERT INTO loyalty_tiers VALUES (3, "STANDARD", false);

INSERT INTO customers VALUES (1, "Priya Sharma", 1, 2340.50);
INSERT INTO customers VALUES (2, "James O'Brien", 2, 890.75);
INSERT INTO customers VALUES (3, "Lena Kim", 3, 149.99);

INSERT INTO products VALUES (1, "PROD-101-ULTRA", "Ultra-Efficient Smart Thermostat", "Home Automation", "energy-saving, smart-home, iot, eco-friendly", 249.99, "Vendor-A", 10, 20);
INSERT INTO products VALUES (2, "PROD-102-ECO", "EcoSmart LED Bulb", "Home Automation", "energy-efficient, led, smart-home, eco-friendly", 199.99, "Vendor-B", 12, 35);
INSERT INTO products VALUES (3, "PROD-505-LTD", "Premium Noise-Cancelling Headphones", "Audio", "premium, headphones, noise-cancelling, audio", 399.99, "Vendor-A", 10, 13);
INSERT INTO products VALUES (4, "PROD-506-ALT", "Bluetooth Over-Ear Headphones", "Audio", "bluetooth, over-ear, headphones, audio", 299.99, "Vendor-B", 12, 5);