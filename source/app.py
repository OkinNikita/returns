from flask import Flask, render_template, request, redirect, flash
from database import get_db
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'secret'

try:
    import init_db
    init_db.init_db()
    print("Database initialized")
except Exception as e:
    print(f"Database init error: {e}")

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/returns', methods=['GET', 'POST'])
def returns_page():
    sellers = get_sellers()

    print(f"DEBUG: Found {len(sellers)} sellers")
    for seller in sellers:
        print(f"DEBUG: Seller - ID: {seller['id']}, Name: {seller['name']}")

    if not sellers:
        flash('No sellers found in database. Please initialize database first.', 'error')
        return render_template('returns.html', returns=[], sellers=[])

    if request.method == 'POST':
        try:
            seller_name = request.form['seller_name']
            customer_name = request.form['customer_name']
            customer_surname = request.form['customer_surname']
            purchase_date = request.form['purchase_date']
            product_name = request.form['product_name']
            reason = request.form['reason']

            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                        INSERT INTO returns
                        (seller_name, customer_name, customer_surname, purchase_date, product_name, reason)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (seller_name, customer_name, customer_surname, purchase_date, product_name, reason))

            conn.commit()
            cur.close()
            conn.close()

            flash('Return created successfully')
            return redirect('/returns')

        except Exception as e:
            flash(f'Error creating return: {e}', 'error')

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM returns ORDER BY id DESC')
    returns = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('returns.html', returns=returns, sellers=sellers)

@app.route('/update/<int:return_id>', methods=['POST'])
def update_return(return_id):
    try:
        status = request.form['status']
        comment = request.form.get('comment', '')

        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE returns SET status = %s, comment = %s WHERE id = %s',
                    (status, comment, return_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Status updated successfully')
    except Exception as e:
        flash(f'Error updating status: {e}', 'error')

    return redirect('/admin')

@app.route('/admin')
def admin():
    sellers = get_sellers()
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM returns ORDER BY id DESC')
    returns = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin.html', returns=returns, sellers=sellers)

if __name__ == '__main__':
    print("Starting Flask application")
    app.run(debug=True, port=5000)