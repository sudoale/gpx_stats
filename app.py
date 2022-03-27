from pathlib import Path
from flask import (Flask,
                   render_template,
                   request,
                   redirect)

from werkzeug.utils import secure_filename

from src.gpx_stats import process_file

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['GET'])
def analyze():
    fn = request.args.get('f')
    segment_time = int(request.args.get('t', '60'))
    data = process_file(fn, segment_time)
    segments = data['segments']
    labels = []
    performance = []
    for item in segments:
        labels.append(item['nr'])
        performance.append(item['performance'])
    return render_template('analyze.html', labels=labels, data=performance)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        if 'file' not in request.files:  # check if the post request has the file part
            return redirect(request.url)
        file = request.files['file']
        filename = secure_filename(file.filename)
        if filename.endswith('gpx'):
            file.save(Path(__file__).parent / 'input' / filename)
            return render_template('analyze.html')


if __name__ == '__main__':
    app.run(debug=True)
