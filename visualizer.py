import seaborn
import matplotlib.pyplot as plt
import pandas
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
#segments = pandas.DataFrame.from_dict(data['segments'], orient='index')
#segments['km'] = segments.index.astype('int') + 1
#segments['min'] = segments.index.astype('int') + 1

#seaborn.set_theme(style='darkgrid')
#seaborn.lineplot(x='min', y='performance', data=segments)
#plt.show()
