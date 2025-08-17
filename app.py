from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import cv2
import numpy as np
from pyzbar import pyzbar
import base64
import io
from PIL import Image
import os
import logging
from database import StudentDatabase
from datetime import datetime
from functools import wraps

# Configure logging for production
if os.environ.get('DEBUG', 'False').lower() != 'true':
    logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-file-size

# MongoDB Configuration (matches your existing setup)
MONGODB_URL = os.environ.get('MONGODB_URL', "mongodb+srv://admin:Admin%40123@cluster0.lgew08w.mongodb.net/Spiro")
DATABASE_NAME = os.environ.get('DATABASE_NAME', "Council")
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', "students")

# Initialize database
db = StudentDatabase()

# Default admin credentials (change these in production)
ADMIN_CREDENTIALS = {
    'username': os.environ.get('ADMIN_USERNAME', 'admin'),
    'password': os.environ.get('ADMIN_PASSWORD', 'password123')
}

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def decode_barcode_from_image(image):
    """
    Decode barcode from image data
    """
    try:
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Decode barcodes
        barcodes = pyzbar.decode(opencv_image)
        
        results = []
        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            # Get barcode location
            (x, y, w, h) = barcode.rect
            
            results.append({
                'data': barcode_data,
                'type': barcode_type,
                'location': {'x': x, 'y': y, 'width': w, 'height': h}
            })
        
        return results
    except Exception as e:
        app.logger.error(f"Error decoding barcode: {str(e)}")
        return []

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == ADMIN_CREDENTIALS['username'] and 
            password == ADMIN_CREDENTIALS['password']):
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Home page with barcode scanning interface"""
    return render_template('index.html')

@app.route('/manual_entry')
@login_required
def manual_entry():
    """Manual student ID entry page"""
    return render_template('manual_entry.html')

@app.route('/manual_register', methods=['POST'])
@login_required
def manual_register():
    """Handle manual student ID registration"""
    try:
        student_id = request.form.get('student_id', '').strip()
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        # Verify student using the same logic as barcode scanning but mark as manual
        result = db.verify_student(student_id, scan_type="manual")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Error processing manual entry: {str(e)}'}), 500

@app.route('/scan', methods=['POST'])
@login_required
def scan_barcode():
    """Handle barcode scanning from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Read image
        image = Image.open(file.stream)
        
        # Decode barcodes
        results = decode_barcode_from_image(image)
        
        if results:
            # Verify each barcode against the database
            verified_results = []
            for barcode in results:
                student_verification = db.verify_student(barcode['data'])
                barcode['verification'] = student_verification
                verified_results.append(barcode)
            
            return jsonify({
                'success': True,
                'barcodes': verified_results,
                'message': f'Found {len(results)} barcode(s) - verified against database'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No barcodes found in the image'
            })
    
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/scan_camera', methods=['POST'])
@login_required
def scan_camera():
    """Handle barcode scanning from camera data"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Decode barcodes
        results = decode_barcode_from_image(image)
        
        if results:
            # Verify each barcode against the database
            verified_results = []
            for barcode in results:
                student_verification = db.verify_student(barcode['data'])
                barcode['verification'] = student_verification
                verified_results.append(barcode)
            
            return jsonify({
                'success': True,
                'barcodes': verified_results,
                'message': f'Found {len(results)} barcode(s) - verified against database'
            })
        else:
            return jsonify({
                'success': False,
                'barcodes': [],
                'message': 'No barcodes found'
            })
    
    except Exception as e:
        return jsonify({'error': f'Error processing camera image: {str(e)}'}), 500

@app.route('/continuous_scan', methods=['POST'])
@login_required
def continuous_scan():
    """Handle continuous barcode scanning from camera stream"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Decode barcodes
        results = decode_barcode_from_image(image)
        
        # Verify barcodes against database if found
        verified_results = []
        if results:
            for barcode in results:
                student_verification = db.verify_student(barcode['data'])
                barcode['verification'] = student_verification
                verified_results.append(barcode)
        
        return jsonify({
            'success': len(results) > 0,
            'barcodes': verified_results,
            'scanning': True
        })
    
    except Exception as e:
        return jsonify({'error': f'Error in continuous scanning: {str(e)}'}), 500

@app.route('/students')
@login_required
def students():
    """Display all students"""
    students = db.get_all_students()
    return render_template('students.html', students=students)

@app.route('/scan_logs')
@login_required
def scan_logs():
    """Display scan logs"""
    logs = db.get_scan_logs()
    return render_template('scan_logs.html', logs=logs)

@app.route('/api/students', methods=['GET'])
def api_get_students():
    """API endpoint to get all students"""
    students = db.get_all_students()
    return jsonify(students)

@app.route('/api/scan_logs', methods=['GET'])
def api_get_scan_logs():
    """API endpoint to get scan logs"""
    logs = db.get_scan_logs()
    return jsonify(logs)

@app.route('/api/verify_student/<student_id>', methods=['GET'])
def api_verify_student(student_id):
    """API endpoint to verify a specific student"""
    result = db.verify_student(student_id)
    return jsonify(result)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db_status = "connected" if db.client else "disconnected"
        
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file"""
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting Council Barcode Registration App")
    print(f"📊 Database: {DATABASE_NAME}")
    print(f"🔗 MongoDB: Connected" if db.client else "Disconnected")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
