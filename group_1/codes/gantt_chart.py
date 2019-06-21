import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd
import warnings
warnings.simplefilter("ignore", UserWarning)


tasks = pd.read_csv('tasks.txt', parse_dates=[1])
tasks.columns = ['task', 'start', 'duration', 'perc']

def row_to_dict(row):
    return dict(Task=str(row['task']),
                Start=str(row['start'].date()),
                Finish=str((row['start'] + pd.DateOffset(row['duration'])).date()),
                Complete=row['perc'])

df = tasks.apply(row_to_dict, axis=1).tolist()

fig = ff.create_gantt(df,colors='RdBu', index_col='Complete',show_colorbar=True)
fig['layout']['xaxis']['rangeselector']['visible'] = False
fig['layout']['xaxis']['rangeslider'] = dict(bgcolor='#E2E2E2')
fig['layout']['xaxis']['type'] = 'date'
fig['layout'].update(autosize=False, width=1200, height=700, margin=dict(l=200))
pio.write_image(fig, 'Gantt.png')
