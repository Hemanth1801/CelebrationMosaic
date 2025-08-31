import os
import json
import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    """Load user submissions from data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    """Save user submissions to data.json"""
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_admin_settings():
    """Load admin settings from admin_settings.json"""
    default_settings = {
        "logo_filename": "logo.png",
        "max_entries": 50,
        "grid_mode": "auto",  # "auto" or "manual"
        "grid_rows": 10,
        "grid_cols": 12,
        "symbols": [
            {"filename": "diya.png", "label": "Diya"},
            {"filename": "cracker.png", "label": "Cracker"},
            {"filename": "rocket.png", "label": "Rocket"}
        ]
    }
    try:
        with open('admin_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # Ensure all required keys exist
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        save_admin_settings(default_settings)
        return default_settings

def save_admin_settings(settings):
    """Save admin settings to admin_settings.json"""
    with open('admin_settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Render the submission form"""
    settings = load_admin_settings()
    return render_template('index.html', symbols=settings['symbols'])

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission"""
    try:
        name = request.form.get('name', '').strip()
        message = request.form.get('message', '').strip()
        symbol = request.form.get('symbol', '').strip()
        
        # Validation
        if not name or not message or not symbol:
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))
        
        if len(name) > 50:
            flash('Name must be 50 characters or less!', 'error')
            return redirect(url_for('index'))
        
        if len(message) > 200:
            flash('Message must be 200 characters or less!', 'error')
            return redirect(url_for('index'))
        
        # Validate symbol is in allowed list
        settings = load_admin_settings()
        valid_symbols = [s['filename'] for s in settings['symbols']]
        if symbol not in valid_symbols:
            flash('Invalid symbol selected!', 'error')
            return redirect(url_for('index'))
        
        # Create new entry with unique ID for position tracking
        new_entry = {
            'id': str(uuid.uuid4()),  # Unique identifier for position consistency
            'name': name,
            'message': message,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
        
        # Load existing data and add new entry
        data = load_data()
        data.append(new_entry)
        
        # Apply max entries limit
        max_entries = settings.get('max_entries', 50)
        if len(data) > max_entries:
            data = data[-max_entries:]  # Keep only the most recent entries
        
        save_data(data)
        
        flash('Your submission has been added to the mosaic!', 'success')
        return redirect(url_for('mosaic', animate='true'))
        
    except Exception as e:
        logging.error(f"Error in submit: {e}")
        flash('An error occurred while submitting your entry.', 'error')
        return redirect(url_for('index'))

@app.route('/mosaic')
def mosaic():
    """Render the mosaic display"""
    try:
        data = load_data()
        settings = load_admin_settings()
        return render_template('mosaic.html', 
                             entries=data, 
                             logo_filename=settings['logo_filename'])
    except Exception as e:
        logging.error(f"Error in mosaic: {e}")
        return render_template('mosaic.html', entries=[], logo_filename='logo.png')

@app.route('/admin')
def admin():
    """Render the admin interface"""
    settings = load_admin_settings()
    data = load_data()
    return render_template('admin.html', 
                         settings=settings, 
                         entry_count=len(data))

@app.route('/admin/upload-logo', methods=['POST'])
def upload_logo():
    """Handle logo upload"""
    try:
        if 'logo' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        file = request.files['logo']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            name, ext = os.path.splitext(filename)
            filename = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Update admin settings
            settings = load_admin_settings()
            settings['logo_filename'] = filename
            save_admin_settings(settings)
            
            flash('Logo uploaded successfully!', 'success')
        else:
            flash('Invalid file type! Please upload PNG, JPG, JPEG, GIF, or SVG files.', 'error')
            
    except Exception as e:
        logging.error(f"Error uploading logo: {e}")
        flash('An error occurred while uploading the logo.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/update-settings', methods=['POST'])
def update_settings():
    """Update admin settings"""
    try:
        settings = load_admin_settings()
        
        # Update max entries
        max_entries = request.form.get('max_entries', type=int)
        if max_entries and max_entries > 0:
            settings['max_entries'] = max_entries
        
        # Update grid settings
        grid_mode = request.form.get('grid_mode', 'auto')
        settings['grid_mode'] = grid_mode
        
        if grid_mode == 'manual':
            grid_rows = request.form.get('grid_rows', type=int)
            grid_cols = request.form.get('grid_cols', type=int)
            
            if grid_rows and grid_rows > 0 and grid_rows <= 50:
                settings['grid_rows'] = grid_rows
            if grid_cols and grid_cols > 0 and grid_cols <= 50:
                settings['grid_cols'] = grid_cols
        
        save_admin_settings(settings)
        flash('Settings updated successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        flash('An error occurred while updating settings.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/add-symbol', methods=['POST'])
def add_symbol():
    """Add a new celebratory symbol"""
    try:
        emoji = request.form.get('emoji', '').strip()
        label = request.form.get('label', '').strip()
        
        if not emoji or not label:
            flash('Both emoji and label are required!', 'error')
            return redirect(url_for('admin'))
        
        settings = load_admin_settings()
        
        # Check if symbol already exists
        for symbol in settings['symbols']:
            if symbol['emoji'] == emoji:
                flash('This symbol already exists!', 'error')
                return redirect(url_for('admin'))
        
        settings['symbols'].append({'emoji': emoji, 'label': label})
        save_admin_settings(settings)
        
        flash('Symbol added successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error adding symbol: {e}")
        flash('An error occurred while adding the symbol.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/remove-symbol', methods=['POST'])
def remove_symbol():
    """Remove a celebratory symbol"""
    try:
        emoji = request.form.get('emoji', '').strip()
        
        if not emoji:
            flash('Invalid symbol!', 'error')
            return redirect(url_for('admin'))
        
        settings = load_admin_settings()
        
        # Don't allow removing all symbols
        if len(settings['symbols']) <= 1:
            flash('Cannot remove the last symbol!', 'error')
            return redirect(url_for('admin'))
        
        settings['symbols'] = [s for s in settings['symbols'] if s['emoji'] != emoji]
        save_admin_settings(settings)
        
        flash('Symbol removed successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error removing symbol: {e}")
        flash('An error occurred while removing the symbol.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/clear-entries', methods=['POST'])
def clear_entries():
    """Clear all user entries"""
    try:
        save_data([])
        flash('All entries have been cleared!', 'success')
    except Exception as e:
        logging.error(f"Error clearing entries: {e}")
        flash('An error occurred while clearing entries.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/api/entries')
def api_entries():
    """API endpoint to get current entries (for real-time updates)"""
    try:
        data = load_data()
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error in api_entries: {e}")
        return jsonify([])

@app.route('/api/admin-settings')
def api_admin_settings():
    """API endpoint to get current admin settings (for logo updates)"""
    try:
        settings = load_admin_settings()
        return jsonify(settings)
    except Exception as e:
        logging.error(f"Error in api_admin_settings: {e}")
        return jsonify({"logo_filename": "logo.png", "max_entries": 50, "symbols": []})

if __name__ == '__main__':
    # Ensure static directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
