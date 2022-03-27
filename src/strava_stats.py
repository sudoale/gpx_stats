import json
from pathlib import Path

HERE = Path(__file__).parent
IN_DIR = HERE.parents[0] / 'output'

def get_stats_from_run(fn, threshold=1800):
    with open(fn, 'r+') as file:
        data = json.loads(file.read())

    filtered = [s['performance'] for s in data['segments'] if s['performance'] >= threshold]

    return filtered


if __name__ == '__main__':
    fn = IN_DIR / 'out_Morning_Run_4_8.json'
    stats = get_stats_from_run(fn)

    print(stats)
    print(sum(stats) / len(stats))

