from pathlib import Path
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)

from werkzeug.utils import secure_filename

from src.gpx_stats import (process_performance_file,
                           process_course_file)
from src.helpers import get_files_of_format

UPLOAD_FOLDER = Path(__file__).parent / 'input'
COURSE_UPLOAD_FOLDER = UPLOAD_FOLDER / 'course'
COURSE_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PERFORMANCE_UPLOAD_FOLDER = UPLOAD_FOLDER / 'performance'
PERFORMANCE_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'gpx'}


app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_file_extension(filename):
    if not (fn_parts := filename.split('.')):
        return None, None
    return fn_parts[0].lower(), fn_parts[1].lower()


def process_file_upload(file, file_type):
    file_prefix, file_extension = get_file_extension(file.filename)
    if file_extension in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename).lower()
        if file_type == 'performance':
            file.save(PERFORMANCE_UPLOAD_FOLDER / filename)
            return url_for('analyze_performance', f=file_prefix, t=60), 200
        elif file_type == 'course':
            file.save(COURSE_UPLOAD_FOLDER / filename)
            return url_for('analyze_performance', f=file_prefix), 200
    return f".{file_extension} files not supported. Please try again.", 400


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', location='home')


@app.route('/course', methods=['GET'])
def course():
    course_files = get_files_of_format(COURSE_UPLOAD_FOLDER, 'gpx')
    return render_template('course.html',
                           location='course',
                           files=course_files)


@app.route('/performance', methods=['GET'])
def performance():
    performance_files = get_files_of_format(PERFORMANCE_UPLOAD_FOLDER, 'gpx')
    return render_template('performance.html',
                           location='performance',
                           files=performance_files)


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


@app.route('/plan/course', methods=['GET'])
def plan_course():
    course = request.args.get('c')
    hours = request.args.get('h')
    minutes = request.args('m')
    total_minutes = (hours * 60) + minutes

    data = process_course_file(course)


@app.route('/upload_performance_file', methods=['POST'])
def upload_performance_file():
    file = request.files['file']
    return process_file_upload(file, 'performance')


@app.route('/upload_course_file', methods=['POST'])
def upload_course_file():
    file = request.files['file']
    return process_file_upload(file, 'course')


@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if request.method == 'POST':
        pass
    else:
        course_files = get_files_of_format(COURSE_UPLOAD_FOLDER, 'gpx')
        return render_template('plan_course.html',
                                files=course_files)


if __name__ == '__main__':
    app.run(debug=True, port=5500)
