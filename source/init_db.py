from database import get_db

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS returns CASCADE')
    cur.execute('DROP TABLE IF EXISTS users CASCADE')

    cur.execute('''
                CREATE TABLE users (
                                       id SERIAL PRIMARY KEY,
                                       name VARCHAR(100),
                                       user_type VARCHAR(20)
                )
                ''')

    cur.execute('''
                CREATE TABLE returns (
                                         id SERIAL PRIMARY KEY,
                                         seller_name VARCHAR(100),
                                         customer_name VARCHAR(100),
                                         customer_surname VARCHAR(100),
                                         purchase_date DATE,
                                         product_name VARCHAR(100),
                                         reason TEXT,
                                         status VARCHAR(20) DEFAULT 'pending',
                                         comment TEXT
                )
                ''')

    sellers = [
        ('John Smith', 'seller'),
        ('Maria Johnson', 'seller'),
        ('Alex Brown', 'seller'),
        ('Emily Davis', 'seller'),
        ('Michael Wilson', 'seller')
    ]

    for seller in sellers:
        cur.execute("INSERT INTO users (name, user_type) VALUES (%s, %s)", seller)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized with sellers")

if __name__ == '__main__':
    init_db()