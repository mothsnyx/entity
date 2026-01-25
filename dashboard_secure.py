from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import Database
import os
import secrets

app = Flask(__name__)
# WICHTIG: Ändere diesen Secret Key!
app.secret_key = secrets.token_hex(32)  # Generiert automatisch einen sicheren Key

# ==================== SICHERHEITS-OPTIONEN ====================

# OPTION 1: HTTP Basic Auth (Einfach, aber sicher genug für privaten Gebrauch)
auth = HTTPBasicAuth()

# Benutzer und Passwörter (Passwörter sind gehasht)
users = {
    "admin": generate_password_hash("sNbt1404."),  # ÄNDERE DIES!
    # Füge weitere Benutzer hinzu:
    # "user2": generate_password_hash("anderes-passwort"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# OPTION 2: Session-basiertes Login (Fortgeschrittener)
LOGIN_ENABLED = True  # Setze auf False um Login zu deaktivieren

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not LOGIN_ENABLED:
            return f(*args, **kwargs)
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== LOGIN ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not LOGIN_ENABLED:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users.get(username), password):
            session['logged_in'] = True
            session['username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!', 'info')
    return redirect(url_for('login'))

# ==================== DATENBANK ====================
db = Database()

# ==================== DASHBOARD ROUTES ====================
# Füge @login_required zu allen Routes hinzu für Session-Login
# ODER nutze @auth.login_required für Basic Auth

@app.route('/')
@login_required  # Session-basiert
# @auth.login_required  # HTTP Basic Auth (kommentiere ein, wenn gewünscht)
def index():
    return render_template('index.html')

@app.route('/realms')
@login_required
def realms():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM realms ORDER BY name")
    realms_list = cursor.fetchall()
    conn.close()
    return render_template('realms.html', realms=realms_list)

@app.route('/realms/add', methods=['POST'])
@login_required
def add_realm():
    realm_name = request.form.get('name')
    if realm_name:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO realms (name) VALUES (?)", (realm_name,))
            conn.commit()
            conn.close()
            flash(f'Realm "{realm_name}" added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('realms'))

@app.route('/realms/delete/<int:realm_id>', methods=['POST'])
@login_required
def delete_realm(realm_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM realms WHERE id = ?", (realm_id,))
        conn.commit()
        conn.close()
        flash('Realm deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('realms'))

@app.route('/realms/edit/<int:realm_id>', methods=['POST'])
@login_required
def edit_realm(realm_id):
    new_name = request.form.get('name')
    if new_name:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE realms SET name = ? WHERE id = ?", (new_name, realm_id))
            conn.commit()
            conn.close()
            flash('Realm updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('realms'))

@app.route('/shop')
@login_required
def shop():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shop_items ORDER BY price")
    items = cursor.fetchall()
    conn.close()
    return render_template('shop.html', items=items)

@app.route('/shop/add', methods=['POST'])
@login_required
def add_shop_item():
    item_name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    
    if item_name and price:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shop_items (item_name, price, description) VALUES (?, ?, ?)",
                         (item_name, int(price), description))
            conn.commit()
            conn.close()
            flash(f'Item "{item_name}" added to shop!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('shop'))

@app.route('/shop/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_shop_item(item_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shop_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash('Shop item deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('shop'))

@app.route('/shop/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_shop_item(item_id):
    item_name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    
    if item_name and price:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE shop_items SET item_name = ?, price = ?, description = ? WHERE id = ?",
                         (item_name, int(price), description, item_id))
            conn.commit()
            conn.close()
            flash('Shop item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('shop'))

@app.route('/trials')
@login_required
def trials():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trial_messages ORDER BY role, id")
    messages = cursor.fetchall()
    conn.close()
    return render_template('trials.html', messages=messages)

@app.route('/trials/add', methods=['POST'])
@login_required
def add_trial_message():
    role = request.form.get('role')
    message = request.form.get('message')
    
    if role and message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trial_messages (role, message) VALUES (?, ?)", (role, message))
            conn.commit()
            conn.close()
            flash(f'Trial message for {role} added!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('trials'))

@app.route('/trials/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_trial_message(message_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trial_messages WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()
        flash('Trial message deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('trials'))

@app.route('/trials/edit/<int:message_id>', methods=['POST'])
@login_required
def edit_trial_message(message_id):
    role = request.form.get('role')
    message = request.form.get('message')
    
    if role and message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE trial_messages SET role = ?, message = ? WHERE id = ?",
                         (role, message, message_id))
            conn.commit()
            conn.close()
            flash('Trial message updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('trials'))

@app.route('/hunting')
@login_required
def hunting():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hunting_items")
    items = cursor.fetchall()
    conn.close()
    return render_template('hunting.html', items=items)

@app.route('/hunting/add', methods=['POST'])
@login_required
def add_hunting_item():
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hunting_items (item_name, message) VALUES (?, ?)",
                         (item_name if item_name else None, message))
            conn.commit()
            conn.close()
            flash('Hunting item added!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('hunting'))

@app.route('/hunting/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_hunting_item(item_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hunting_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash('Hunting item deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('hunting'))

@app.route('/hunting/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_hunting_item(item_id):
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE hunting_items SET item_name = ?, message = ? WHERE id = ?",
                         (item_name if item_name else None, message, item_id))
            conn.commit()
            conn.close()
            flash('Hunting item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('hunting'))

@app.route('/fishing')
@login_required
def fishing():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fishing_items")
    items = cursor.fetchall()
    conn.close()
    return render_template('fishing.html', items=items)

@app.route('/fishing/add', methods=['POST'])
@login_required
def add_fishing_item():
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO fishing_items (item_name, message) VALUES (?, ?)",
                         (item_name if item_name else None, message))
            conn.commit()
            conn.close()
            flash('Fishing item added!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('fishing'))

@app.route('/fishing/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_fishing_item(item_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fishing_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash('Fishing item deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('fishing'))

@app.route('/fishing/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_fishing_item(item_id):
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE fishing_items SET item_name = ?, message = ? WHERE id = ?",
                         (item_name if item_name else None, message, item_id))
            conn.commit()
            conn.close()
            flash('Fishing item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('fishing'))

@app.route('/scavenging')
@login_required
def scavenging():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scavenging_items")
    items = cursor.fetchall()
    conn.close()
    return render_template('scavenging.html', items=items)

@app.route('/scavenging/add', methods=['POST'])
@login_required
def add_scavenging_item():
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scavenging_items (item_name, message) VALUES (?, ?)",
                         (item_name if item_name else None, message))
            conn.commit()
            conn.close()
            flash('Scavenging item added!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('scavenging'))

@app.route('/scavenging/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_scavenging_item(item_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scavenging_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        flash('Scavenging item deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('scavenging'))

@app.route('/scavenging/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_scavenging_item(item_id):
    item_name = request.form.get('item_name')
    message = request.form.get('message')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE scavenging_items SET item_name = ?, message = ? WHERE id = ?",
                         (item_name if item_name else None, message, item_id))
            conn.commit()
            conn.close()
            flash('Scavenging item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('scavenging'))

@app.route('/profiles')
@login_required
def profiles():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles ORDER BY name")
    profiles_list = cursor.fetchall()
    conn.close()
    return render_template('profiles.html', profiles=profiles_list)

# ==================== IP WHITELIST (Optional) ====================
# Aktiviere dies, um nur bestimmte IPs zuzulassen
ENABLE_IP_WHITELIST = False
ALLOWED_IPS = ['127.0.0.1', '192.168.1.100']  # Füge erlaubte IPs hinzu

@app.before_request
def limit_remote_addr():
    if ENABLE_IP_WHITELIST:
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            return "Access Denied", 403

if __name__ == '__main__':
    # Erstelle templates folder
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # SICHERHEITS-EINSTELLUNGEN:
    # 1. Nur lokal: host='127.0.0.1'
    # 2. Im Netzwerk: host='0.0.0.0' (mit Login-Schutz!)
    # 3. Production: debug=False
    
    print("="*50)
    print("🔒 SICHERHEITS-HINWEISE:")
    print("="*50)
    print(f"Login aktiviert: {LOGIN_ENABLED}")
    print(f"Standard-Benutzer: admin")
    print(f"⚠️  ÄNDERE DAS PASSWORT in Zeile 18!")
    print("="*50)
    
    # Für lokalen Zugriff (nur du):
    # app.run(debug=True, host='127.0.0.1', port=5000)
    
    # Für Netzwerk-Zugriff (mit Login):
    app.run(debug=True, host='0.0.0.0', port=5000)
