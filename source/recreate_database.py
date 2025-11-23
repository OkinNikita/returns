from database import get_db

def recreate_database():
    conn = get_db()
    cur = conn.cursor()

    print("Recreating database tables")

    cur.execute("DROP TABLE IF EXISTS returns CASCADE")
    cur.execute("DROP TABLE IF EXISTS customers CASCADE")
    cur.execute("DROP TABLE IF EXISTS users CASCADE")

    cur.execute('''
                CREATE TABLE users (
                                       id SERIAL PRIMARY KEY,
                                       name VARCHAR(100) NOT NULL,
                                       user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('seller', 'admin')),
                                       email VARCHAR(100) UNIQUE,
                                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
    print("Created 'users' table")

    cur.execute('''
                CREATE TABLE customers (
                                           id SERIAL PRIMARY KEY,
                                           first_name VARCHAR(100) NOT NULL,
                                           last_name VARCHAR(100) NOT NULL,
                                           email VARCHAR(100),
                                           phone VARCHAR(20),
                                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
    print("Created 'customers' table")

    cur.execute('''
                CREATE TABLE returns (
                                         id SERIAL PRIMARY KEY,
                                         seller_id INTEGER NOT NULL,
                                         customer_id INTEGER NOT NULL,
                                         admin_id INTEGER,
                                         purchase_date DATE NOT NULL,
                                         product_name VARCHAR(100) NOT NULL,
                                         reason TEXT NOT NULL,
                                         status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
                                         comment TEXT,
                                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                         CONSTRAINT fk_returns_seller
                                             FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE RESTRICT,

                                         CONSTRAINT fk_returns_customer
                                             FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,

                                         CONSTRAINT fk_returns_admin
                                             FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
                )
                ''')
    print("Created 'returns' table with foreign keys")

    print("Adding sample data")

    users_data = [
        ('John Smith', 'seller', 'john.smith@store.com'),
        ('Maria Johnson', 'seller', 'maria.johnson@store.com'),
        ('Alex Brown', 'seller', 'alex.brown@store.com'),
        ('Emily Davis', 'seller', 'emily.davis@store.com'),
        ('Admin User', 'admin', 'admin@store.com')
    ]

    for name, user_type, email in users_data:
        cur.execute(
            "INSERT INTO users (name, user_type, email) VALUES (%s, %s, %s)",
            (name, user_type, email)
        )
        print(f"Added user: {name}")

    customers_data = [
        ('Michael', 'Johnson', 'michael.johnson@email.com', '+1-555-0101'),
        ('Sarah', 'Williams', 'sarah.williams@email.com', '+1-555-0102'),
        ('David', 'Miller', 'david.miller@email.com', '+1-555-0103'),
        ('Lisa', 'Anderson', 'lisa.anderson@email.com', '+1-555-0104'),
        ('Robert', 'Taylor', 'robert.taylor@email.com', '+1-555-0105')
    ]

    for first_name, last_name, email, phone in customers_data:
        cur.execute(
            "INSERT INTO customers (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, phone)
        )
        print(f"Added customer: {first_name} {last_name}")

    returns_data = [
        (1, 1, None, '2024-01-15', 'MacBook Pro 16"', 'Screen has dead pixels', 'pending', None),
        (2, 2, None, '2024-01-12', 'iPhone 15 Pro', 'Battery draining too fast', 'pending', None),
        (3, 3, None, '2024-01-10', 'Samsung Galaxy S24', 'Camera not focusing properly', 'pending', None),
        (1, 4, None, '2024-01-08', 'Sony WH-1000XM5', 'Right earphone not working', 'pending', None),
        (2, 5, None, '2024-01-05', 'iPad Air', 'Touch screen unresponsive', 'pending', None)
    ]

    for seller_id, customer_id, admin_id, purchase_date, product_name, reason, status, comment in returns_data:
        cur.execute(
            "INSERT INTO returns (seller_id, customer_id, admin_id, purchase_date, product_name, reason, status, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (seller_id, customer_id, admin_id, purchase_date, product_name, reason, status, comment)
        )
        print(f"Added return: {product_name}")

    conn.commit()
    cur.close()
    conn.close()

    print("Database recreated successfully with all tables and relationships")

if __name__ == '__main__':
    recreate_database()