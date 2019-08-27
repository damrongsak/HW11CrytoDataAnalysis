import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.style as style
style.use('seaborn-poster')  # sets the size of the charts
style.use('ggplot')

pair = 'ethusd'
path = 'data'
bin_size = '1h'

filename = '{}/{}_{}.xlsx'.format(path, pair, bin_size)
sheet_name = pair
df = pd.read_excel(filename, sheet_name=sheet_name, index_col='time')

min_price = df['close'].min(axis=0, skipna=True)
max_price = df['close'].max(axis=0, skipna=True)

date_start = df[0:1].index[0]
date_end = df[-1:].index[0]
price = df[-1:].close.values[0]
zone = df[-1:].zone.values[0]
atr = df[-1:].atr.values[0]

zone_len = 500 if max_price > 5000 else 25  # manage zone

# Calculate Zone
df['zone'] = df['close'].apply(lambda x: (x-(x % zone_len)))

df_time_in_the_zone = df.groupby('zone').count()[['close']]
df_time_in_the_zone.rename(columns={'close': 'count_point'}, inplace=True)
# point * 60min * 60sec
df_time_in_the_zone['time_sec'] = df_time_in_the_zone['count_point'] * 60 * 60
df_time_in_the_zone['str_time'] = df_time_in_the_zone['time_sec'].apply(
    lambda x: str(datetime.timedelta(seconds=x)))

# Setup Chart
fig, ax = plt.subplots(figsize=(15, 6))

for idx, row in df_time_in_the_zone.iterrows():
    close = df.loc[df.zone == idx].close.values[0]
    close = close - (close % zone_len)
    cur_zone = '>> ATR:%s ' % int(atr) if (
        price - (price % zone_len)) == close else ''
    label = '{}Z:{} T:{}'.format(cur_zone, str(int(idx)), row.str_time)

    x = df.loc[df.zone == idx].close.values
    y = df.loc[df.zone == idx].atr.values
    scale = 15

    ax.scatter(x, y, s=scale, label=label, alpha=0.3,
               edgecolors='white', cmap='Accent', marker="o")

ax.legend(bbox_to_anchor=(1, 1), fontsize='large')
ax.grid(True)

plt.xlabel('close')
plt.ylabel('ATR')
plt.title('{} {} from {} to {}@{} zone:{} atr:{}'.format(pair.upper(), bin_size, date_start,
                                                         date_end, price, int(zone), round(atr, 2)), fontsize=16)
plt.xticks(range(int(min_price), int(max_price), zone_len))
plt.xticks(fontsize=10, rotation=45)
plt.tick_params(axis='both', which='minor', labelsize=10)
# plt.savefig('data/{pair}.png'.format(pair=pair))

plt.show()
