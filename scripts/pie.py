import pandas as pd
import datetime

from bokeh.models import MultiChoice, Panel
from bokeh.layouts import layout
from bokeh.models import CustomJS, DatePicker

from math import pi
from bokeh.plotting import figure
from bokeh.transform import cumsum


# create dataframe
def pie_visualization(df):
    def convert_timestamp(time):
        return datetime.datetime.fromtimestamp(time / 1000).date()

    df['tanggal'] = df['tanggal'].apply(convert_timestamp)

    df2 = df[['tanggal', 'KASUS', 'PROVINSI']].copy()

    # create multi choice

    OPTIONS = ["Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Selatan", "Kalimantan Utara", "Sulawesi Barat",
               "Maluku Utara", "Riau", "DI Yogyakarta", "Papua", "Papua Barat", "Kalimantan Timur", "Bengkulu", "Aceh",
               "Sumatera Utara", "Kep. Bangka Belitung", "Sumatera Barat",
               "Lampung", "Dki Jakarta", "Jawa Tengah", "Kepulauan Riau", "Bali", "Kalimantan Barat",
               "Kalimantan Tengah", "Sulawesi Utara", "Jambi", "Sulawesi Tengah", "Gorontalo", "Jawa Barat",
               "Jawa Timur", "Maluku", "Sulawesi Selatan", "Sumatera Selatan", "Banten", "Sulawesi Tenggara"]

    multi_choice = MultiChoice(
        value=["Dki Jakarta", "Jawa Barat", "Jawa Tengah"], options=OPTIONS)
    multi_choice.js_on_change("value", CustomJS(code="""
        console.log('multi_choice: value=' + this.value, this.toString())
    """))

    # create date picker

    date_picker = DatePicker(title='Select date', value="2021-12-29",
                             min_date="2021-05-01", max_date="2022-01-06")
    date_picker.js_on_change("value", CustomJS(code="""
        console.log('date_picker: value=' + this.value, this.toString())
    """))

    # create new dataset from original data

    dframe = df2.loc[df2['tanggal'] == pd.to_datetime(date_picker.value)]
    dframe.reset_index(drop=True, inplace=True)
    count = len(dframe['PROVINSI'])
    for i in range(count):
        provinsi = dframe['PROVINSI'][i]
        replace = dframe['PROVINSI'][i].title()
        dframe['PROVINSI'] = dframe['PROVINSI'].replace([provinsi], replace)

    count = len(dframe['PROVINSI'])
    choice = len(multi_choice.value)

    # create ditionary

    Dict = {}

    for i in range(count):
        for j in range(choice):
            if dframe['PROVINSI'][i] == multi_choice.value[j - 1]:
                Dict[dframe['PROVINSI'][i]] = dframe['KASUS'][i]

    # create pie chart

    chart_colors = ['#fff2cc', '#a6d5be', '#d5a6bd',
                    '#00b4b4', '#929fd1', '#9ad3ca',
                    '#483d8b', '#b0c4de', '#46697b',
                    '#99ac06', '#ff9400', '#01e1ec',
                    '#412c39', '#a56d67', '#62a586',
                    '#326448', '#9620a4', '#bf9a5a',
                    '#772d22', '#45980c', '#c98938',
                    '#e9705a', '#ffc000', '#002060',
                    '#54d157', '#5faca1', '#541d8b',
                    '#e82cb5', '#14b437', '#79eb00']

    data = pd.Series(Dict).reset_index(
        name='value').rename(columns={'index': 'country'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = chart_colors[:len(Dict)]

    p = figure(height=350, title="Pie Chart", toolbar_location=None,
               tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    lay_out = layout([multi_choice], [date_picker], [p])

    tab = Panel(child=lay_out, title="Lineplot")

    return tab
