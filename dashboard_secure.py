from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import Database
import os
import secrets
import subprocess
import threading
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ==================== SECURITY OPTIONS ====================
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("sNbt1404."),
    "mod": generate_password_hash("hkp35e."),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

LOGIN_ENABLED = True

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

# ==================== DATABASE ====================
db = Database()

# ==================== DASHBOARD ROUTES ====================

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ==================== UPDATE / DEPLOY ROUTE ====================

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_SERVICE = "dbdbot"
DASHBOARD_SERVICE = "dbddashboard"

def _restart_services(restart_dashboard):
    subprocess.run(["sudo", "systemctl", "restart", BOT_SERVICE])
    if restart_dashboard:
        subprocess.run(["sudo", "systemctl", "restart", DASHBOARD_SERVICE])

@app.route('/admin/update', methods=['POST'])
@login_required
def admin_update():
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = (result.stdout + result.stderr).strip()

        if result.returncode != 0:
            flash(f"git pull failed: {output}", "danger")
            return redirect(url_for('index'))

        if "Already up to date" in output:
            flash("Already up to date — nothing to restart.", "info")
            return redirect(url_for('index'))

        dashboard_changed = "dashboard_secure.py" in output
        flash(f"Pulled latest changes, restarting service(s)...\n{output}", "success")
        threading.Timer(1.5, _restart_services, args=(dashboard_changed,)).start()
        return redirect(url_for('index'))
    except subprocess.TimeoutExpired:
        flash("git pull timed out after 30 seconds.", "danger")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

# ==================== REALMS ROUTES ====================

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

# ==================== SHOP ROUTES ====================

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
    category = request.form.get('category', 'Miscellaneous')
    currency_type = request.form.get('currency_type', 'bloodpoints')
    
    if item_name and price:
        try:
            item_name = db.normalise(item_name)
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shop_items (item_name, price, description, category, currency_type) VALUES (?, ?, ?, ?, ?)",
                         (item_name, int(price), description, category, currency_type))
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
    category = request.form.get('category', 'Miscellaneous')
    currency_type = request.form.get('currency_type', 'bloodpoints')
    
    if item_name and price:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE shop_items SET item_name = ?, price = ?, description = ?, category = ?, currency_type = ? WHERE id = ?",
                         (item_name, int(price), description, category, currency_type, item_id))
            conn.commit()
            conn.close()
            flash('Shop item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('shop'))

# ==================== TRIALS ROUTES ====================

@app.route('/trials')
@login_required
def trials():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trial_messages ORDER BY performance_level, role, id")
    messages = cursor.fetchall()
    conn.close()
    return render_template('trials.html', messages=messages)

@app.route('/trials/add', methods=['POST'])
@login_required
def add_trial_message():
    role = request.form.get('role')
    performance_level = request.form.get('performance_level')
    message = request.form.get('message')
    
    if role and performance_level is not None and message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trial_messages (role, performance_level, message) VALUES (?, ?, ?)", 
                         (role, int(performance_level), message))
            conn.commit()
            conn.close()
            flash(f'Trial message for {role} (Level {performance_level}) added!', 'success')
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
    performance_level = request.form.get('performance_level')
    message = request.form.get('message')
    
    if role and performance_level is not None and message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE trial_messages SET role = ?, performance_level = ?, message = ? WHERE id = ?",
                         (role, int(performance_level), message, message_id))
            conn.commit()
            conn.close()
            flash('Trial message updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('trials'))

# ==================== HUNTING ROUTES ====================

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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            if item_name:
                item_name = db.normalise(item_name)
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hunting_items (item_name, message, category, description, sell_value, weight, difficulty, flee_message, fail_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message))
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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE hunting_items SET item_name = ?, message = ?, category = ?, description = ?, sell_value = ?, weight = ?, difficulty = ?, flee_message = ?, fail_message = ? WHERE id = ?",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message, item_id))
            conn.commit()
            conn.close()
            flash('Hunting item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('hunting'))

# ==================== FISHING ROUTES ====================

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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            if item_name:
                item_name = db.normalise(item_name)
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO fishing_items (item_name, message, category, description, sell_value, weight, difficulty, flee_message, fail_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message))
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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE fishing_items SET item_name = ?, message = ?, category = ?, description = ?, sell_value = ?, weight = ?, difficulty = ?, flee_message = ?, fail_message = ? WHERE id = ?",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message, item_id))
            conn.commit()
            conn.close()
            flash('Fishing item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('fishing'))

# ==================== SCAVENGING ROUTES ====================

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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            if item_name:
                item_name = db.normalise(item_name)
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scavenging_items (item_name, message, category, description, sell_value, weight, difficulty, flee_message, fail_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message))
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
    category = request.form.get('category', 'Miscellaneous')
    description = request.form.get('description')
    sell_value = request.form.get('sell_value', 0)
    weight = request.form.get('weight', 10)
    difficulty = request.form.get('difficulty', 10)
    flee_message = request.form.get('flee_message', '')
    fail_message = request.form.get('fail_message', '')
    
    if message:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE scavenging_items SET item_name = ?, message = ?, category = ?, description = ?, sell_value = ?, weight = ?, difficulty = ?, flee_message = ?, fail_message = ? WHERE id = ?",
                         (item_name if item_name else None, message, category if item_name else None, description, sell_value, weight, difficulty, flee_message, fail_message, item_id))
            conn.commit()
            conn.close()
            flash('Scavenging item updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('scavenging'))

# ==================== PROFILES ROUTES ====================

# ==================== RESERVATIONS ROUTES ====================

@app.route('/reservations')
@login_required
def reservations():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations WHERE active = 1 ORDER BY expires_at ASC")
    reservations_list = cursor.fetchall()
    conn.close()
    return render_template('reservations.html', reservations=reservations_list)

@app.route('/reservations/create', methods=['POST'])
@login_required
def create_reservation_dashboard():
    guild_id = '1308318260944568340'
    channel_id = request.form.get('channel_id')
    user_id = request.form.get('user_id')
    hours = request.form.get('hours')
    title = request.form.get('title') or "📅 Reservation Active"
    description = request.form.get('description') or None
    color = request.form.get('color', '#000000').lstrip('#')
    image_url = request.form.get('image_url') or None
    thumbnail_url = request.form.get('thumbnail_url') or None

    if not (channel_id and user_id and hours):
        flash('Channel ID, User ID and duration are required!', 'danger')
        return redirect(url_for('reservations'))

    try:
        hours = float(hours)
        if hours <= 0 or hours > 336:
            flash('Duration must be between 0 and 336 hours (14 days)!', 'danger')
            return redirect(url_for('reservations'))
    except ValueError:
        flash('Duration must be a number!', 'danger')
        return redirect(url_for('reservations'))

    reservation_id, expires_at = db.create_reservation(
        guild_id, channel_id, user_id, title, description, color,
        None, image_url, thumbnail_url, hours
    )

    try:
        import requests
        bot_url = "http://localhost:5002/send_reservation"
        payload = {
            'channel_id': channel_id,
            'user_id': user_id,
            'reservation_id': reservation_id,
            'title': title,
            'description': description,
            'color': color,
            'expires_at': expires_at,
            'image_url': image_url,
            'thumbnail_url': thumbnail_url
        }
        response = requests.post(bot_url, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('message_id')
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE reservations SET message_id = ? WHERE id = ?", (message_id, reservation_id))
            conn.commit()
            conn.close()
            flash('Reservation created and posted!', 'success')
        else:
            flash(f'Reservation saved, but failed to post embed: {response.text}', 'danger')
    except Exception as e:
        flash(f'Reservation saved, but failed to post embed: {str(e)}', 'danger')

    return redirect(url_for('reservations'))

@app.route('/reservations/delete/<int:reservation_id>', methods=['POST'])
@login_required
def delete_reservation_dashboard(reservation_id):
    success, message = db.delete_reservation(reservation_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('reservations'))

# ==================== ACTIVITY CHECK ROUTES ====================

@app.route('/activity-check')
@login_required
def activity_check():
    import datetime
    current_month = datetime.datetime.now().strftime('%Y-%m')
    month = request.args.get('month', current_month)

    characters = db.get_all_activity_characters()
    statuses = db.get_activity_statuses_for_month(month)
    all_months = db.get_all_checked_months()
    if current_month not in all_months:
        all_months = [current_month] + all_months
    inactive_list = db.get_inactive_characters_for_month(month)

    return render_template(
        'activity_check.html',
        characters=characters,
        statuses=statuses,
        all_months=all_months,
        selected_month=month,
        current_month=current_month,
        inactive_list=inactive_list
    )

@app.route('/activity-check/add-character', methods=['POST'])
@login_required
def add_activity_character():
    character_name = request.form.get('character_name')
    role = request.form.get('role')
    discord_username = request.form.get('discord_username')
    discord_user_id = request.form.get('discord_user_id')
    month = request.form.get('month')

    if not character_name:
        flash('Character name is required!', 'danger')
        return redirect(url_for('activity_check', month=month))

    success, message = db.add_activity_character(character_name, role, discord_username, discord_user_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('activity_check', month=month))

@app.route('/activity-check/remove-character/<int:character_id>', methods=['POST'])
@login_required
def remove_activity_character(character_id):
    month = request.form.get('month')
    success, message = db.remove_activity_character(character_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('activity_check', month=month))

@app.route('/activity-check/set-status', methods=['POST'])
@login_required
def set_activity_status():
    character_id = request.form.get('character_id')
    month = request.form.get('month')
    status = request.form.get('status')

    if not (character_id and month and status):
        flash('Missing data for status update!', 'danger')
        return redirect(url_for('activity_check', month=month))

    success, message = db.set_activity_status(int(character_id), month, status)
    if not success:
        flash(message, 'danger')
    return redirect(url_for('activity_check', month=month))

@app.route('/profiles')
@login_required
def profiles():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles ORDER BY name")
    profiles_list = cursor.fetchall()
    conn.close()
    return render_template('profiles.html', profiles=profiles_list)

@app.route('/profiles/delete/<int:profile_id>', methods=['POST'])
@login_required
def delete_profile_dashboard(profile_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        # Get name first for the flash message
        cursor.execute("SELECT name FROM profiles WHERE id = ?", (profile_id,))
        result = cursor.fetchone()
        if not result:
            flash('Profile not found!', 'danger')
            conn.close()
            return redirect(url_for('profiles'))
        profile_name = result[0]
        # Delete profile and their inventory
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        cursor.execute("DELETE FROM inventory WHERE character_name = ?", (profile_name,))
        conn.commit()
        conn.close()
        flash(f'Profile "{profile_name}" and their inventory deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('profiles'))

# ==================== EMBEDS ROUTES (Separated from Reaction Roles) ====================

@app.route('/embeds')
@login_required
def embeds():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM embeds ORDER BY id DESC")
    embeds_list = cursor.fetchall()
    
    # Get welcome message settings
    cursor.execute("SELECT * FROM welcome_settings WHERE id = 1")
    welcome_settings = cursor.fetchone()
    
    conn.close()
    return render_template('embeds.html', embeds=embeds_list, welcome_settings=welcome_settings)

@app.route('/embeds/welcome/settings', methods=['POST'])
@login_required
def update_welcome_settings():
    enabled = request.form.get('enabled') == '1'
    embed_id = request.form.get('embed_id')
    channel_id = request.form.get('channel_id')
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""INSERT OR REPLACE INTO welcome_settings (id, enabled, embed_id, channel_id)
                         VALUES (1, ?, ?, ?)""", (enabled, embed_id if embed_id else None, channel_id))
        conn.commit()
        conn.close()
        flash('Welcome settings updated!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('embeds'))

@app.route('/embeds/create', methods=['POST'])
@login_required
def create_embed():
    name = request.form.get('name')
    title = request.form.get('title')
    description = request.form.get('description')
    color = request.form.get('color', '#000000').lstrip('#')
    footer_text = request.form.get('footer_text')
    image_url = request.form.get('image_url')
    thumbnail_url = request.form.get('thumbnail_url')
    
    # Handle file uploads
    if 'image_file' in request.files:
        image_file = request.files['image_file']
        if image_file and image_file.filename:
            try:
                import requests
                bot_url = "http://localhost:5002/upload_image"
                files = {'file': (image_file.filename, image_file.stream, image_file.mimetype)}
                response = requests.post(bot_url, files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result.get('url')
                    flash('Image uploaded successfully!', 'success')
                else:
                    flash(f'Failed to upload image: {response.text}', 'danger')
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'danger')
    
    if 'thumbnail_file' in request.files:
        thumbnail_file = request.files['thumbnail_file']
        if thumbnail_file and thumbnail_file.filename:
            try:
                import requests
                bot_url = "http://localhost:5002/upload_image"
                files = {'file': (thumbnail_file.filename, thumbnail_file.stream, thumbnail_file.mimetype)}
                response = requests.post(bot_url, files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    thumbnail_url = result.get('url')
                    flash('Thumbnail uploaded successfully!', 'success')
                else:
                    flash(f'Failed to upload thumbnail: {response.text}', 'danger')
            except Exception as e:
                flash(f'Error uploading thumbnail: {str(e)}', 'danger')
    
    if name:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO embeds 
                            (name, title, description, color, footer_text, image_url, thumbnail_url) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (name, title, description, color, footer_text, image_url, thumbnail_url))
            conn.commit()
            conn.close()
            flash(f'Embed "{name}" created!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('embeds'))

@app.route('/embeds/edit/<int:embed_id>', methods=['POST'])
@login_required
def edit_embed(embed_id):
    name = request.form.get('name')
    title = request.form.get('title')
    description = request.form.get('description')
    color = request.form.get('color', '#000000').lstrip('#')
    footer_text = request.form.get('footer_text')
    image_url = request.form.get('image_url')
    thumbnail_url = request.form.get('thumbnail_url')
    
    if name:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE embeds SET 
                            name = ?, title = ?, description = ?, color = ?, 
                            footer_text = ?, image_url = ?, thumbnail_url = ?
                            WHERE id = ?""",
                         (name, title, description, color, footer_text, image_url, thumbnail_url, embed_id))
            conn.commit()
            conn.close()
            flash('Embed updated!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('embeds'))

@app.route('/embeds/delete/<int:embed_id>', methods=['POST'])
@login_required
def delete_embed(embed_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM embeds WHERE id = ?", (embed_id,))
        conn.commit()
        conn.close()
        flash('Embed deleted!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('embeds'))

@app.route('/embeds/send/<int:embed_id>', methods=['POST'])
@login_required
def send_embed(embed_id):
    channel_id = request.form.get('channel_id')
    
    if not channel_id:
        flash('Channel ID is required!', 'danger')
        return redirect(url_for('embeds'))
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM embeds WHERE id = ?", (embed_id,))
        embed_data = cursor.fetchone()
        
        if not embed_data:
            flash('Embed not found!', 'danger')
            return redirect(url_for('embeds'))
        
        import requests
        bot_url = "http://localhost:5002/send_embed"
        
        payload = {
            'channel_id': channel_id,
            'embed_id': embed_id,
            'title': embed_data[2],
            'description': embed_data[3],
            'color': embed_data[4],
            'footer_text': embed_data[5],
            'image_url': embed_data[6],
            'thumbnail_url': embed_data[7],
            'reaction_roles': []  # No reaction roles from embeds page
        }
        
        response = requests.post(bot_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('message_id')
            
            cursor.execute("UPDATE embeds SET channel_id = ?, message_id = ? WHERE id = ?",
                         (channel_id, message_id, embed_id))
            conn.commit()
            flash('Embed sent to channel!', 'success')
        else:
            flash(f'Failed to send embed: {response.text}', 'danger')
        
        conn.close()
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('embeds'))

@app.route('/embeds/update/<int:embed_id>', methods=['POST'])
@login_required
def update_embed_message(embed_id):
    try:
        # Get embed data
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM embeds WHERE id = ?", (embed_id,))
        embed_data = cursor.fetchone()
        
        if not embed_data or not embed_data[9]:  # Check if message_id exists
            flash('Embed not sent yet or message ID not found!', 'danger')
            return redirect(url_for('embeds'))
        
        # Send update request to bot API
        import requests
        bot_url = "http://localhost:5002/update_embed"
        
        payload = {
            'channel_id': embed_data[8],
            'message_id': embed_data[9],
            'title': embed_data[2],
            'description': embed_data[3],
            'color': embed_data[4],
            'footer_text': embed_data[5],
            'image_url': embed_data[6],
            'thumbnail_url': embed_data[7]
        }
        
        response = requests.post(bot_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            flash('Embed updated in channel!', 'success')
        else:
            flash(f'Failed to update embed: {response.text}', 'danger')
        
        conn.close()
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('embeds'))

# ==================== REACTION ROLES ROUTES (Separate from Embeds) ====================

@app.route('/reaction-roles')
@login_required
def reaction_roles():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get all embeds for selection
    cursor.execute("SELECT * FROM embeds ORDER BY id DESC")
    embeds_list = cursor.fetchall()
    
    # Get all reaction role messages with their details
    cursor.execute("""
        SELECT DISTINCT rr.message_id, e.name as embed_name
        FROM reaction_roles rr
        LEFT JOIN embeds e ON e.message_id = rr.message_id
        GROUP BY rr.message_id
    """)
    messages = cursor.fetchall()
    
    # Build reaction messages list with roles
    reaction_messages = []
    for msg in messages:
        message_id = msg[0]
        embed_name = msg[1] or 'Unknown Embed'
        
        # Get all roles for this message
        cursor.execute("SELECT emoji, role_id FROM reaction_roles WHERE message_id = ?", (message_id,))
        roles = [{'emoji': r[0], 'role_id': r[1]} for r in cursor.fetchall()]
        
        reaction_messages.append({
            'message_id': message_id,
            'embed_name': embed_name,
            'roles': roles
        })
    
    conn.close()
    return render_template('reaction_roles.html', embeds=embeds_list, reaction_messages=reaction_messages)

@app.route('/reaction-roles/create', methods=['POST'])
@login_required
def create_reaction_role():
    embed_id = request.form.get('embed_id')
    channel_id = request.form.get('channel_id')
    emojis = request.form.getlist('emoji[]')
    role_ids = request.form.getlist('role_id[]')
    
    if not embed_id or not channel_id:
        flash('Embed and Channel ID are required!', 'danger')
        return redirect(url_for('reaction_roles'))
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM embeds WHERE id = ?", (embed_id,))
        embed_data = cursor.fetchone()
        
        if not embed_data:
            flash('Embed not found!', 'danger')
            return redirect(url_for('reaction_roles'))
        
        # Build reaction roles list
        reaction_roles = []
        for emoji, role_id in zip(emojis, role_ids):
            if emoji and role_id:
                reaction_roles.append({'emoji': emoji, 'role_id': role_id})
        
        if not reaction_roles:
            flash('At least one reaction role mapping is required!', 'danger')
            return redirect(url_for('reaction_roles'))
        
        # Send to bot
        import requests
        bot_url = "http://localhost:5002/send_embed"
        
        payload = {
            'channel_id': channel_id,
            'embed_id': embed_id,
            'title': embed_data[2],
            'description': embed_data[3],
            'color': embed_data[4],
            'footer_text': embed_data[5],
            'image_url': embed_data[6],
            'thumbnail_url': embed_data[7],
            'reaction_roles': reaction_roles
        }
        
        response = requests.post(bot_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('message_id')
            
            # Update embed with channel and message ID
            cursor.execute("UPDATE embeds SET channel_id = ?, message_id = ? WHERE id = ?",
                         (channel_id, message_id, embed_id))
            
            # Save reaction roles to database
            for rr in reaction_roles:
                cursor.execute("INSERT OR REPLACE INTO reaction_roles (message_id, emoji, role_id) VALUES (?, ?, ?)",
                             (message_id, rr['emoji'], rr['role_id']))
            
            conn.commit()
            flash(f'Reaction role message created with {len(reaction_roles)} role(s)!', 'success')
        else:
            flash(f'Failed to send reaction role message: {response.text}', 'danger')
        
        conn.close()
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('reaction_roles'))

@app.route('/reaction-roles/edit-embed/<message_id>', methods=['POST'])
@login_required
def edit_reaction_role_embed(message_id):
    """Edit the embed content for an existing reaction role message and update it live in Discord."""
    title = request.form.get('title')
    description = request.form.get('description')
    color = request.form.get('color', '#000000').lstrip('#')
    footer_text = request.form.get('footer_text')
    image_url = request.form.get('image_url')
    thumbnail_url = request.form.get('thumbnail_url')

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Find the embed linked to this message_id
        cursor.execute("SELECT id, channel_id FROM embeds WHERE message_id = ?", (message_id,))
        embed_row = cursor.fetchone()

        if not embed_row:
            flash('No embed found linked to this reaction role message!', 'danger')
            conn.close()
            return redirect(url_for('reaction_roles'))

        embed_id = embed_row[0]
        channel_id = embed_row[1]

        # Update the embed in the database
        cursor.execute("""UPDATE embeds SET
                        title = ?, description = ?, color = ?,
                        footer_text = ?, image_url = ?, thumbnail_url = ?
                        WHERE id = ?""",
                     (title, description, color, footer_text, image_url, thumbnail_url, embed_id))
        conn.commit()
        conn.close()

        # Push the update live to Discord via bot API
        import requests as req
        bot_url = "http://localhost:5002/update_embed"
        payload = {
            'channel_id': channel_id,
            'message_id': message_id,
            'title': title,
            'description': description,
            'color': color,
            'footer_text': footer_text,
            'image_url': image_url,
            'thumbnail_url': thumbnail_url
        }
        response = req.post(bot_url, json=payload, timeout=10)

        if response.status_code == 200:
            flash('Reaction role embed updated successfully in Discord!', 'success')
        else:
            flash(f'Embed saved to database but failed to update in Discord: {response.text}', 'warning')

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('reaction_roles'))

@app.route('/reaction-roles/update-roles/<message_id>', methods=['POST'])
@login_required
def update_reaction_role_mappings(message_id):
    """Update the emoji→role mappings for an existing reaction role message."""
    emojis = request.form.getlist('emoji[]')
    role_ids = request.form.getlist('role_id[]')

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Find the embed linked to this message_id for channel info
        cursor.execute("SELECT channel_id FROM embeds WHERE message_id = ?", (message_id,))
        embed_row = cursor.fetchone()

        if not embed_row:
            flash('No embed found linked to this reaction role message!', 'danger')
            conn.close()
            return redirect(url_for('reaction_roles'))

        channel_id = embed_row[0]

        # Delete old role mappings
        cursor.execute("DELETE FROM reaction_roles WHERE message_id = ?", (message_id,))

        # Insert new mappings
        new_roles = []
        for emoji, role_id in zip(emojis, role_ids):
            if emoji and role_id:
                cursor.execute("INSERT INTO reaction_roles (message_id, emoji, role_id) VALUES (?, ?, ?)",
                             (message_id, emoji, role_id))
                new_roles.append({'emoji': emoji, 'role_id': role_id})

        conn.commit()
        conn.close()

        # Update reactions on the Discord message via bot API
        import requests as req
        bot_url = "http://localhost:5002/update_reactions"
        payload = {
            'channel_id': channel_id,
            'message_id': message_id,
            'reaction_roles': new_roles
        }
        response = req.post(bot_url, json=payload, timeout=10)

        if response.status_code == 200:
            flash(f'Reaction role mappings updated with {len(new_roles)} role(s)!', 'success')
        else:
            # Mappings saved in DB even if Discord sync fails
            flash(f'Mappings saved but failed to sync reactions in Discord: {response.text}', 'warning')

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('reaction_roles'))

@app.route('/reaction-roles/delete/<message_id>', methods=['POST'])
@login_required
def delete_reaction_role(message_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reaction_roles WHERE message_id = ?", (message_id,))
        conn.commit()
        conn.close()
        flash('Reaction roles deleted from message!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('reaction_roles'))

# ==================== IP WHITELIST (Optional) ====================
ENABLE_IP_WHITELIST = False
ALLOWED_IPS = ['127.0.0.1', '192.168.1.100']

@app.before_request
def limit_remote_addr():
    if ENABLE_IP_WHITELIST:
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            return "Access Denied", 403

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("="*50)
    print("🔒 SECURITY NOTES:")
    print("="*50)
    print(f"Login enabled: {LOGIN_ENABLED}")
    print(f"Default user: admin")
    print(f"⚠️  CHANGE PASSWORD in line 18!")
    print("="*50)
    
    # debug=False in production: debug mode starts the auto-reloader, which
    # runs a SECOND copy of this process — a second writer to the SQLite file
    # that can cause 'database is locked' errors.
    app.run(debug=False, host='0.0.0.0', port=5000)
