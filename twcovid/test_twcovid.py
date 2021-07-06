import tcdata, tcplot
import pprint

tcdata.refresh_data_from_json()
df = tcdata.get_twcovid_df_from_db()
pprint.pprint(df)

fig = tcplot.plot_confirm_case(df)
fig.show()


