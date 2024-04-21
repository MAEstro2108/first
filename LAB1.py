from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import DecimalField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfjdMEpAAAAAGl1maz1txad8oVIUJ8q7-mFiHjd'
app.config['UPLOAD_FOLDER'] = 'uploads'

class ResizeForm(FlaskForm):
    scale = DecimalField('Scale:', validators=[InputRequired()], places=2)
    recaptcha = RecaptchaField(public_key='6LfjdMEpAAAAAGl1maz1txad8oVIUJ8q7-mFiHjd')
    submit = SubmitField('Resize')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ResizeForm()
    if form.validate_on_submit():
        scale = form.scale.data
        if 'image' in request.files:
            image = request.files['image']
            if image.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                resized_image_path = resize_image(filepath, scale)
                original_colors = get_colors(filepath)
                resized_colors = get_colors(resized_image_path)
                return render_template('result.html', original=original_colors, resized=resized_colors)
    return render_template('index.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def resize_image(filepath, scale):
    img = Image.open(filepath)
    new_size = tuple(int(x * scale) for x in img.size)
    resized_img = img.resize(new_size, Image.ANTIALIAS)
    resized_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resized_' + os.path.basename(filepath))
    resized_img.save(resized_image_path)
    return resized_image_path

def get_colors(filepath):
    img = Image.open(filepath)
    colors = img.getcolors(img.size[0]*img.size[1])
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:10]  # Top 10 colors
    hex_colors = [rgb_to_hex(color[1]) for color in sorted_colors]
    return hex_colors

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

if __name__ == '__main__':
    app.run(debug=True)