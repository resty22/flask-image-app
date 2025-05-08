from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    error = None
    filename = None

    if request.method == 'POST':
        if 'image' not in request.files:
            error = 'Tidak ada file yang diunggah.'
        else:
            file = request.files['image']
            if file.filename == '':
                error = 'File belum dipilih.'
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                # Buka gambar
                pil_img = Image.open(filepath).convert('RGB')
                img_np = np.array(pil_img)
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                # Ambil aksi dan parameter
                action = request.form.get('action')
                angle = request.form.get('angle')

                if action == 'crop':
                    print("Menerapkan crop...")
                    width, height = pil_img.size
                    left = width // 4
                    top = height // 4
                    right = width * 3 // 4
                    bottom = height * 3 // 4
                    pil_img = pil_img.crop((left, top, right, bottom))
                    img_np = np.array(pil_img)
                    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                elif action == 'blur':
                    print("Menerapkan blur...")
                    img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)

                elif action == 'contrast':
                    print("Meningkatkan kontras...")
                    pil_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                    enhancer = ImageEnhance.Contrast(pil_img)
                    pil_img = enhancer.enhance(1.5)
                    img_np = np.array(pil_img)
                    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                elif action == 'rotate':
                    try:
                        angle = int(angle)
                    except (TypeError, ValueError):
                        angle = 90
                    print(f"Rotasi {angle} derajat...")
                    (h, w) = img_cv.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    img_cv = cv2.warpAffine(img_cv, M, (w, h))

                elif action == 'resize':
                    print("Resize ke 50%...")
                    height, width = img_cv.shape[:2]
                    img_cv = cv2.resize(img_cv, (width // 2, height // 2))

                elif action == 'sobel':
                    print("Deteksi tepi dengan Sobel...")
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                    sobel = cv2.magnitude(sobelx, sobely)
                    img_cv = cv2.cvtColor(np.uint8(sobel), cv2.COLOR_GRAY2BGR)

                elif action == 'roberts':
                    print("Deteksi tepi dengan Roberts...")
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    kernel_x = np.array([[1, 0], [0, -1]])
                    kernel_y = np.array([[0, 1], [-1, 0]])
                    roberts_x = cv2.filter2D(gray, -1, kernel_x)
                    roberts_y = cv2.filter2D(gray, -1, kernel_y)
                    roberts = np.sqrt(roberts_x**2 + roberts_y**2)
                    img_cv = cv2.cvtColor(np.uint8(roberts), cv2.COLOR_GRAY2BGR)

                elif action == 'prewitt':
                    print("Deteksi tepi dengan Prewitt...")
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
                    kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
                    prewitt_x = cv2.filter2D(gray, -1, kernelx)
                    prewitt_y = cv2.filter2D(gray, -1, kernely)
                    prewitt = cv2.magnitude(prewitt_x.astype(np.float32), prewitt_y.astype(np.float32))
                    img_cv = cv2.cvtColor(np.uint8(prewitt), cv2.COLOR_GRAY2BGR)

                elif action == 'canny':
                    print("Deteksi tepi dengan Canny...")
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, 100, 200)
                    img_cv = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

                # Simpan gambar hasil
                output_filename = 'processed_' + file.filename
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                final_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                final_img.save(output_path)
                filename = output_filename

    return render_template('index.html', error=error, filename=filename)

@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
