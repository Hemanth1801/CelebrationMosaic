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

def get_available_positions():
    """Get a list of available grid positions"""
    settings = load_admin_settings()
    total_positions = settings['grid_rows'] * settings['grid_cols']
    data = load_data()
    
    # Create set of all used positions
    used_positions = set()
    for entry in data:
        if 'position' in entry:
            used_positions.add(entry['position'])
    
    # Return list of available positions
    return [pos for pos in range(total_positions) if pos not in used_positions]

def load_admin_settings():
    """Load admin settings from admin_settings.json"""
    default_settings = {
        "logo_filename": "logo.png",
        "short_logo_filename": "logo_20250902_001306.png",  # Default short logo
        "header_text": "Happy Diwali",  # Default header text
        "max_entries": 50,
        "celebration_animations": ["confetti", "fireworks", "diwali", "sparkle-rain", "flower-burst", "rangoli"],  # All animations enabled by default
        "color_scheme": {
            "submission_page": {
                "background": "#000000",
                "text": "#ffffff",
                "heading_text": "#ffcc00",
                "form_background": "#1a1a1a",
                "form_border": "#333333",
                "input_background": "#2a2a2a",
                "input_text": "#ffffff",
                "input_border": "#404040",
                "input_focus_border": "#ffcc00",
                "label_text": "#cccccc",
                "button_primary_bg": "#ffcc00",
                "button_primary_text": "#000000",
                "button_primary_hover_bg": "#ffd633",
                "button_secondary_bg": "#404040",
                "button_secondary_text": "#ffffff",
                "button_secondary_hover_bg": "#4d4d4d",
                "alert_success_bg": "#28a745",
                "alert_success_text": "#ffffff",
                "alert_error_bg": "#dc3545",
                "alert_error_text": "#ffffff",
                "symbol_selector_bg": "#2a2a2a",
                "symbol_selector_border": "#404040",
                "symbol_selector_active": "#ffcc00"
            },
            "mosaic_page": {
                "background": "#000000",
                "text": "#ffffff",
                "tile_background": "#333333",
                "tile_text": "#ffffff",
                "tile_border": "#ffcc00"
            }
        },
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
                # Special handling for celebration_animations
                elif key == 'celebration_animations' and not settings[key]:
                    # If celebration_animations is empty, use default values
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
    return render_template('index.html', 
                         symbols=settings['symbols'], 
                         admin_settings=settings,
                         settings=settings,  # Pass settings both ways for compatibility
                         body_class='entry-page')

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
        
        # Get available positions
        available_positions = get_available_positions()
        if not available_positions:
            flash('The mosaic is currently full!', 'error')
            return redirect(url_for('index'))
            
        # Randomly select a position from available positions
        import random
        position = random.choice(available_positions)
        
        # Create new entry with unique ID and assigned position
        new_entry = {
            'id': f'tile-{position + 1}',  # Position-based ID for better tracking
            'name': name,
            'message': message,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'position': position  # Store the assigned position
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
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error in submit: {e}")
        flash('An error occurred while submitting your entry.', 'error')
        return redirect(url_for('index'))

@app.route('/mosaic')
def mosaic():
    """Render the mosaic display"""
    try:
        settings = load_admin_settings()
        data = load_data()
        # Calculate total needed tiles based on grid
        total_tiles = settings['grid_rows'] * settings['grid_cols']
        # Take only the most recent entries that match the grid size
        entries = data[-total_tiles:] if len(data) >= total_tiles else data
        return render_template('mosaic.html', 
                             entries=entries, 
                             logo_filename=settings['logo_filename'],
                             admin_settings=settings,
                             settings=settings,  # Pass settings as both admin_settings and settings for compatibility
                             body_class='mosaic-page')
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
                         admin_settings=settings,  # Pass settings both ways for compatibility
                         entry_count=len(data),
                         body_class='admin-page')

@app.route('/admin/upload-color-scheme', methods=['POST'])
def upload_color_scheme():
    """Handle color scheme upload"""
    try:
        if 'color_scheme' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        file = request.files['color_scheme']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        if file and file.filename.endswith('.json'):
            try:
                # Read and validate the color scheme
                color_scheme = json.load(file)
                
                # Validate required sections and fields
                required_sections = ['submission_page', 'mosaic_page']
                required_submission_fields = ['background', 'text', 'button', 'button_text']
                required_mosaic_fields = ['background', 'text', 'tile_background', 'tile_text', 'tile_border']
                
                # Check structure
                if not all(section in color_scheme for section in required_sections):
                    flash('Invalid color scheme format! Missing required sections.', 'error')
                    return redirect(url_for('admin'))
                
                # Check submission page fields
                if not all(field in color_scheme['submission_page'] for field in required_submission_fields):
                    flash('Invalid submission page color scheme! Missing required fields.', 'error')
                    return redirect(url_for('admin'))
                
                # Check mosaic page fields
                if not all(field in color_scheme['mosaic_page'] for field in required_mosaic_fields):
                    flash('Invalid mosaic page color scheme! Missing required fields.', 'error')
                    return redirect(url_for('admin'))
                
                # Validate color codes (simple hex validation)
                for section in color_scheme.values():
                    for color in section.values():
                        if not color.startswith('#') or not all(c in '0123456789ABCDEFabcdef' for c in color[1:]):
                            flash('Invalid color code format! Use hex colors (e.g., #FF0000).', 'error')
                            return redirect(url_for('admin'))
                
                # Update settings with new color scheme
                settings = load_admin_settings()
                settings['color_scheme'] = color_scheme
                save_admin_settings(settings)
                
                flash('Color scheme updated successfully!', 'success')
            except json.JSONDecodeError:
                flash('Invalid JSON file!', 'error')
        else:
            flash('Invalid file type! Please upload a JSON file.', 'error')
            
    except Exception as e:
        logging.error(f"Error uploading color scheme: {e}")
        flash('An error occurred while uploading the color scheme.', 'error')
    
    return redirect(url_for('admin'))

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
        
        logo_type = request.form.get('logo_type', 'main')  # 'main' or 'short'
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            name, ext = os.path.splitext(filename)
            filename = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Update admin settings
            settings = load_admin_settings()
            if logo_type == 'short':
                settings['short_logo_filename'] = filename
            else:
                settings['logo_filename'] = filename
            save_admin_settings(settings)
            
            flash(f'{"Short" if logo_type == "short" else "Main"} logo uploaded successfully!', 'success')
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
        
        # Update header text
        header_text = request.form.get('header_text', '').strip()
        if header_text:
            settings['header_text'] = header_text
        
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
        
        # Update celebration animations
        celebration_animations = request.form.getlist('celebration_animations[]')
        # Default to confetti if none selected
        if not celebration_animations:
            celebration_animations = ['confetti']
        # Validate animation types
        valid_animations = ['confetti', 'fireworks', 'diwali', 'sparkle-rain', 'flower-burst', 'rangoli']
        celebration_animations = [anim for anim in celebration_animations if anim in valid_animations]
        settings['celebration_animations'] = celebration_animations
        
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
        if 'symbol_file' not in request.files:
            flash('Symbol image file is required!', 'error')
            return redirect(url_for('admin'))

        file = request.files['symbol_file']
        label = request.form.get('label', '').strip()

        if file.filename == '' or not label:
            flash('Both symbol file and label are required!', 'error')
            return redirect(url_for('admin'))

        if not file.filename.lower().endswith('.png'):
            flash('Only PNG files are allowed for symbols!', 'error')
            return redirect(url_for('admin'))

        settings = load_admin_settings()

        # Create a unique filename for the symbol
        filename = secure_filename(f"symbol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        # Ensure the symbols directory exists
        symbols_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'symbols')
        os.makedirs(symbols_dir, exist_ok=True)

        # Save the file
        file_path = os.path.join(symbols_dir, filename)
        file.save(file_path)

        # Add the symbol to settings
        settings['symbols'].append({'filename': filename, 'label': label})
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
        filename = request.form.get('filename', '').strip()

        if not filename:
            flash('Invalid symbol!', 'error')
            return redirect(url_for('admin'))

        settings = load_admin_settings()

        # Don't allow removing all symbols
        if len(settings['symbols']) <= 1:
            flash('Cannot remove the last symbol!', 'error')
            return redirect(url_for('admin'))

        # Find and remove the symbol file
        symbol_path = os.path.join(app.config['UPLOAD_FOLDER'], 'symbols', filename)
        try:
            os.remove(symbol_path)
        except FileNotFoundError:
            # If file doesn't exist, just log it but continue
            logging.warning(f"Symbol file not found: {symbol_path}")

        # Update settings
        settings['symbols'] = [s for s in settings['symbols'] if s['filename'] != filename]
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
    # Ensure static and symbols directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'symbols'), exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
