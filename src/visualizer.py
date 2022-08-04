import json

fns = ['Morning_run', 'Lunch_Run']

for fn in fns:
    with open(f'out_{fn}.json', 'r') as file:
        data = json.loads(file.read())

    performances = []
    gaps = []
    
    for i, segment in enumerate(data['segments']):
        if segment['performance'] > 1800:
            performances.append(segment['performance'])
            gaps.append(segment['gap'])
            print(i, segment)
    print(f'Average performance: {sum(performances) / len(performances)}')
    print(f'Average gap: {sum(gaps) / len(gaps)}')
