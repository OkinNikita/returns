from flask import Flask, render_template, request, redirect, flash
from database import get_db
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

try:
    import init_db
    init_db.init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")

def get_sellers():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE user_type = 'seller'")
        sellers = cur.fetchall()
        cur.close()
        conn.close()
        return sellers
    except Exception as e:
        print(f"Error getting sellers: {e}")
        return []

def get_customers():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM customers")
        customers = cur.fetchall()
        cur.close()
        conn.close()
        return customers
    except Exception as e:
        print(f"Error getting customers: {e}")
        return []

def get_returns_with_relations():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('''
                    SELECT
                        r.*,
                        s.name as seller_name,
                        c.first_name as customer_first_name,
                        c.last_name as customer_last_name,
                        a.name as admin_name
                    FROM returns r
                             LEFT JOIN users s ON r.seller_id = s.id
                             LEFT JOIN customers c ON r.customer_id = c.id
                             LEFT JOIN users a ON r.admin_id = a.id
                    ORDER BY r.created_at DESC
                    ''')
        returns = cur.fetchall()
        cur.close()
        conn.close()
        return returns
    except Exception as e:
        print(f"Error getting returns: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/returns', methods=['GET', 'POST'])
def returns_page():
    sellers = get_sellers()
    customers = get_customers()

    if request.method == 'POST':
        try:
            seller_id = request.form['seller_id']
            customer_id = request.form['customer_id']
            purchase_date = request.form['purchase_date']
            product_name = request.form['product_name']
            reason = request.form['reason']

            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                        INSERT INTO returns
                            (seller_id, customer_id, purchase_date, product_name, reason)
                        VALUES (%s, %s, %s, %s, %s)
                        ''', (seller_id, customer_id, purchase_date, product_name, reason))

            conn.commit()
            cur.close()
            conn.close()

            flash('Return request created successfully', 'success')
            return redirect('/returns')

        except Exception as e:
            flash(f'Error creating return: {e}', 'error')

    returns = get_returns_with_relations()
    return render_template('returns.html', returns=returns, sellers=sellers, customers=customers)

@app.route('/update_return/<int:return_id>', methods=['POST'])
def update_return(return_id):
    try:
        status = request.form['status']
        comment = request.form.get('comment', '')

        admin_id = 5

        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
                    UPDATE returns
                    SET status = %s, comment = %s, admin_id = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    ''', (status, comment, admin_id, return_id))

        conn.commit()
        cur.close()
        conn.close()

        flash('Return status updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating return: {e}', 'error')

    return redirect('/admin')

@app.route('/admin')
def admin():
    returns = get_returns_with_relations()
    sellers = get_sellers()
    customers = get_customers()
    return render_template('admin.html', returns=returns, sellers=sellers, customers=customers)

if __name__ == '__main__':
    print("Starting Returns Management System")
    app.run(debug=True,host='0.0.0.0', port=5000)