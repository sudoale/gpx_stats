from pathlib import Path
from flask import (Flask,
                   render_template,
                   request)

from werkzeug.utils import secure_filename

from src.gpx_stats import (process_performance_file,
                           process_course_file)

UPLOAD_FOLDER = Path(__file__).parent / 'input'
ALLOWED_EXTENSIONS = {'gpx'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_file_extension(filename):
    if not (fn_parts := filename.split('.')):
        return None, None
    return fn_parts[0].lower(), fn_parts[1].lower()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/analyze/performance', methods=['GET'])
def analyze_performance():
    fn = request.args.get('f')
    segment_time = int(request.args.get('t', '60'))
    data = process_performance_file(fn, segment_time)
    segments = data['segments']
    labels = []
    performance = []
    for item in segments:
        labels.append(item['nr'])
        performance.append(item['performance'])
    return render_template('analyze_performance.html', labels=labels, data=performance)


@app.route('/analyze/course', methods=['GET'])
def analyze_course():
    fn = request.args.get('f')
    data = process_course_file(fn)
    return render_template('analyze_course.html', data=data)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_prefix, file_extenstion = get_file_extension(file.filename)
    if file_extenstion in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        file.save(UPLOAD_FOLDER / filename)
        return f"http://localhost:5000/analyze/performance?f={file_prefix}&t=60", 200
    return f".{file_extenstion} files not supported. Please try again.", 400




if __name__ == '__main__':
    app.run(debug=True)
