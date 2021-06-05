import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("taiwan_covid_cdc.csv")
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# fillin the number of previous day, if no correction -- forward fill
df = df.ffill(axis=1)
df.plot(stacked=False)
plt.show()

# calculate the correction amount and sum to check against the accounced the daily correction number
corr = df.diff(axis=1)
ax = sns.boxplot(data=corr)
plt.show()


dailycorr = pd.concat([corr.iloc[:, i].shift(i) for i in range(corr.shape[1])], axis=1).sum(axis=1)
dailycorr.rename("daily.correction", inplace = True)
print (dailycorr)

# create report, including 7 days rolling avg
summary = pd.concat([df.min(axis=1),df.max(axis=1),df.max(axis=1).rolling(7).mean()], axis=1)
summary.rename(columns = {0:'orginal',1:'after correction',2:'7days rolloing avg'}, inplace = True)
print(summary)
ax = summary.plot(stacked=False)
plt.show()