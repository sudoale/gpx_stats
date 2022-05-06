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


def process_file_upload(file, file_type):
    file_prefix, file_extenstion = get_file_extension(file.filename)
    if file_extenstion in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        file.save(UPLOAD_FOLDER / filename)
        if file_type == 'performance':
            return f"http://localhost:5000/analyze/performance?f={file_prefix}&t=60", 200
        elif file_type == 'course':
            return f"http://localhost:5000/analyze/course?f={file_prefix}", 200
    return f".{file_extenstion} files not supported. Please try again.", 400


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', location='home')


@app.route('/course', methods=['GET'])
def course():
    return render_template('course.html', location='course')


@app.route('/performance', methods=['GET'])
def performance():
    return render_template('performance.html', location='performance')


@app.route('/analyze/performance', methods=['GET'])
def analyze_performance():
    fn = request.args.get('f')
    segment_time = int(request.args.get('t', 0))
    segment_distance = int(request.args.get('d', 0))
    if segment_time:
        data = process_performance_file(fn, segment_time=segment_time)
        return render_template('analyze_performance.html',
                               data=data,
                               activity_name=fn,
                               segment_time=segment_time)
    elif segment_distance:
        data = process_performance_file(fn, segment_distance=segment_distance)
        return render_template('analyze_performance.html',
                               data=data,
                               activity_name=fn,
                               segment_distance=segment_distance)


@app.route('/analyze/course', methods=['GET'])
def analyze_course():
    fn = request.args.get('f')
    data = process_course_file(fn)
    return render_template('analyze_course.html', data=data, activity_name=fn)


@app.route('/upload_performance_file', methods=['POST'])
def upload_performance_file():
    file = request.files['file']
    return process_file_upload(file, 'performance')


@app.route('/upload_course_file', methods=['POST'])
def upload_course_file():
    file = request.files['file']
    return process_file_upload(file, 'course')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
