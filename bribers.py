import pandas as pd

bribes_df = pd.read_csv('data/rounds-bribes.csv')
bribes = list(bribes_df.columns)
bribes.remove('round')
with open('data/bribers.csv', 'w') as f:
    for bribe in bribes:
        f.write(bribe)
        f.write('\n')
