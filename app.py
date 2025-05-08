import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimum 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def manipulate_image(filepath):
    with Image.open(filepath) as img:
        # Resize
        img = img.resize((300, 300))

        # Rotate
        img = img.rotate(90)

        # Crop
        width, height = img.size
        left = width / 4
        top = height / 4
        right = width * 3 / 4
        bottom = height * 3 / 4
        img = img.crop((left, top, right, bottom))

        img.save(filepath)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            manipulate_image(filepath)
            return render_template('index.html', filename=filename)
        else:
            return render_template('index.html', error="File tidak valid. Harus berupa gambar.")
    return render_template('index.html')

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
