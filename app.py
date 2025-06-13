from flask import Flask, render_template, request, redirect
import os
from text import process_video

app = Flask(__name__)
UPLOAD_FOLDER = 'input_videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']
    if file.filename == '':
        return redirect(request.url)
    if file:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'sample.mp4')
        file.save(filepath)
        extracted_text = process_video(filepath)
        return render_template('result.html', transcription=extracted_text)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


