import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_json('./final_target_data.json')

gamer_name = "龙宫公主"

# df_match = df[df['gamerName'] == gamer_name]
df_match = df
time = pd.to_datetime(df['gameCreation']/1000, unit='s')
data_at14_dpm = df_match['at14dpm']
data_af14_dpm = df_match['af14dpm']
data_at14_dtpm = df_match['at14dtpm']
data_af14_dtpm = df_match['af14dtpm']

colors = ['blue' if value else 'red' for value in df_match['targetWin']]

fig, axes = plt.subplots(2, 2, figsize = (6,6), sharex=True)

axes[0, 0].scatter(time, data_at14_dpm, c=colors, s=8)
axes[0, 0].set_title('Damage Per Minute (upto 14m)')
axes[0, 0].grid(True)
axes[0, 1].scatter(time, data_at14_dtpm, c=colors, s=8)
axes[0, 1].set_title('DamageTaken Per Minute (upto 14m)')
axes[0, 1].grid(True)

axes[1, 0].scatter(time, data_af14_dpm, c=colors, s=8)
axes[1, 0].set_title('Damage Per Minute (upto 14m)')
axes[1, 0].grid(True)
axes[1, 1].scatter(time, data_af14_dtpm, c=colors, s=8)
axes[1, 1].set_title('DamageTaken Per Minute (upto 14m)')
axes[1, 1].grid(True)

plt.show()