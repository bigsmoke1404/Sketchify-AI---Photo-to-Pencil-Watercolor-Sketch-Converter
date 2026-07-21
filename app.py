import os
import uuid
import glob
from flask import Flask, render_template, request, jsonify, url_for, session
from werkzeug.utils import secure_filename
from utils.sketch import pencil_sketch, watercolor_sketch

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sketchify_ai' # Required for session

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'outputs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # Enforce 10MB limit

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Basic cleanup to prevent infinite growth (optional but good for a project)"""
    pass # In a real app we might delete files older than 1 hour

@app.route('/')
def index():
    if 'history' not in session:
        session['history'] = []
    return render_template('index.html', history=session['history'])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG'}), 400

    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}.{ext}"
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = f"out_{unique_id}.{ext}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Get filter settings
        filter_type = request.form.get('filter_type', 'pencil')
        
        if filter_type == 'pencil':
            intensity = float(request.form.get('intensity', 0.5))
            edge = float(request.form.get('edge_strength', 0.5))
            pencil_sketch(input_path, output_path, intensity, edge)
        elif filter_type == 'watercolor':
            smoothness = float(request.form.get('smoothness', 0.5))
            watercolor_sketch(input_path, output_path, smoothness)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        # Construct URLs for frontend
        input_url = url_for('static', filename=f"uploads/{filename}")
        output_url = url_for('static', filename=f"outputs/{output_filename}")
        
        # Add to history
        history = session.get('history', [])
        history.insert(0, {'original': input_url, 'result': output_url, 'filter': filter_type.capitalize()})
        session['history'] = history[:5]  # Keep last 5
        
        return jsonify({
            'success': True,
            'original_image': input_url,
            'converted_image': output_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # use_reloader=False prevents the Windows crash where Flask's stat reloader
    # causes exit code 1 immediately after startup on PowerShell.
    # threaded=True allows concurrent requests (important for image processing).
    app.run(debug=True, use_reloader=False, threaded=True)
