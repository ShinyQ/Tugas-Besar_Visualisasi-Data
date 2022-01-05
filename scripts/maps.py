import json

from bokeh.models import (ColumnDataSource, CategoricalColorMapper, Panel,
                          GeoJSONDataSource, ColorBar, TableColumn, HoverTool, Slider)

from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import Button, DataTable
from bokeh.layouts import row, WidgetBox


def maps_covid(covid19, indonesia):
    # Mengkategorikan Ukuran Jumlah Kasus Baru COVID-19
    def category_covid(df):
        if df == 0:
            category = '0'
        elif 1 <= df <= 19:
            category = '1 - 19'
        elif 20 <= df <= 99:
            category = '20 - 99'
        elif 100 <= df <= 999:
            category = '100 - 999'
        elif 1000 <= df <= 2999:
            category = '1000 - 2999'
        elif 3000 <= df <= 9999:
            category = '3000 - 9999'
        elif 10000 <= df <= 99999:
            category = '10000 - 29999'
        elif 30000 <= df <= 99999:
            category = '30000 - 99999'

        return category

    def map_date():
        date_to_day = {}
        date = sorted(covid19['tanggal'].unique())

        for j, val in enumerate(date):
            date_to_day[val] = j + 1

        return date_to_day

    def json_data(selected_day):
        sd = selected_day

        # Pull selected year
        df_dt = covid19.loc[covid19['day'] == sd]

        # Merge the GeoDataframe object (sf) with the covid19 data
        merge = indonesia.merge(df_dt, how='left', left_on=['PROVINSI'], right_on=['PROVINSI'])
        merge['PROVINSI'] = merge['PROVINSI'].str.title()

        # remove columns
        merge.dropna(inplace=True)

        # Bokeh uses geojson formatting, representing geographical   features, with json
        # Convert to json
        merge_json = json.loads(merge.to_json())

        # Convert to json preferred string-like object
        json_data = json.dumps(merge_json)
        return json_data

    def column_data(selected_day):
        cd = selected_day

        column = covid19.loc[covid19['day'] == cd]
        column = column.sort_values(by='KASUS', ascending=False)

        rank = []
        for counter in range(column.index.shape[0]):
            rank.append(counter + 1)

        column['rank'] = rank

        most_confirmed = column.head(20)
        most_confirmed['PROVINSI'] = most_confirmed['PROVINSI'].str.title()

        new_source = dict(
            rank=[rank for rank in most_confirmed['rank']],
            provinsi=[country for country in most_confirmed['PROVINSI']],
            confirmed=[confirmed for confirmed in most_confirmed['KASUS']],
            tanggal=[tanggal for tanggal in most_confirmed['tanggal']],
        )

        return new_source

    def update_plot(attr, old, new):
        day = slider.value
        new_data = json_data(day)
        geosource.geojson = new_data
        source.data = column_data(day)

    def animate_update():
        val = slider.value + 1
        if val > 365:
            val = 0

        slider.value = val

    def animate():
        global callback_id
        if button.label == '► Play':
            button.label = '❚❚ Pause'
            callback_id = curdoc().add_periodic_callback(animate_update, 200)
        else:
            button.label = '► Play'
            curdoc().remove_periodic_callback(callback_id)

    # Membuat kolom pengkategorian jumlah kasus COVID-19
    covid19['category'] = covid19['KASUS'].apply(category_covid)

    # Membuat perhitungan hari untuk setiap tanggal
    covid19['day'] = covid19['tanggal'].map(map_date())

    # Mengambil centroid koordinat
    indonesia['point'] = indonesia['geometry'].centroid

    # Mengambil koordinat x dan y dari point geometry data geospatial
    point_x, point_y = [], []
    for i in range(len(indonesia['point'])):
        point_x.append(indonesia['point'][i].x)
        point_y.append(indonesia['point'][i].y)

    # Menyimpan koordinat point x dan y
    indonesia['x'] = point_x
    indonesia['y'] = point_y

    # Menghapus kolom point dan merename kolom provinsi
    indonesia.drop(columns='point', inplace=True)
    indonesia = indonesia.rename(columns={'Provinsi': 'PROVINSI'})

    # Membuat data source informasi awal untuk maps
    geosource = GeoJSONDataSource(geojson=json_data(1))

    # Membuat data informasi kasus COVID-19 awal untuk tabel
    source = ColumnDataSource(column_data(1))

    list_category = [
        '0', '1 - 19', '20 - 99', '100 - 999', '1000 - 2999',
        '3000 - 9999', '10000 - 29999', '30000 - 99999'
    ]

    # Membuat list yang berisi warna untuk heatmap
    palet = ['#67000d', '#cb181d', '#ef3b2c', '#fc9272', '#fcbba1', '#f7dada', '#fcf2f2', '#ffffff']
    palet = palet[::-1]

    # Menggunakan kategorikal color mapper sebagai pewarnaan heatmap tiap provinsi
    color_mapper = CategoricalColorMapper(factors=list_category, palette=palet)

    # Menampilkan legend categorical mapper
    color_bar = ColorBar(
        color_mapper=color_mapper,
        title_text_font_style='bold',
        title_text_font_size='12px',
        title_text_align='center',
        orientation='vertical',
        major_label_text_font_size='12px',
        major_label_text_font_style='bold',
    )

    # Make a slider object: slider
    slider = Slider(title='Hari Ke', start=1, end=365, step=1, value=1)
    slider.on_change('value', update_plot)

    # Create figure object.
    r = figure(title="", plot_height=500, plot_width=1200, toolbar_location='below', tools=['pan, wheel_zoom, reset'])

    r.title.align = 'center'
    r.xaxis.visible = False
    r.yaxis.visible = False
    r.xgrid.grid_line_color = None
    r.ygrid.grid_line_color = None

    # Add patch renderer to figure.
    states = r.patches(
        'xs', 'ys', source=geosource,
        fill_color={'field': 'category', 'transform': color_mapper},
        line_color='gray',
        line_width=0.25,
        fill_alpha=1,
    )

    # membuat hover
    r.add_tools(HoverTool(
        renderers=[states],
        tooltips=[
            ('Tanggal', '@tanggal'),
            ('Provinsi', '@PROVINSI'),
            ('Terkonfirmasi', '@KASUS{,}'),
            ('Sembuh', '@SEMBUH{,}'),
            ('Meninggal', '@MENINGGAL{,}')
        ]
    ))

    # membuat tombol animasi
    callback_id = None
    button = Button(label='► Play', width=60)
    button.on_click(animate)

    # membuat tabel
    columns = [
        TableColumn(field='rank', title='No.'),
        TableColumn(field='provinsi', title='Provinsi'),
        TableColumn(field='confirmed', title='Terkonfirmasi'),
    ]

    tabel = DataTable(
        source=source, columns=columns, width=300,
        height=600, index_position=None
    )

    # Make a column layout of widgetbox(slider) and plot, and add it to the current document
    r.add_layout(color_bar)

    layout = row(WidgetBox(slider, tabel, button), r)
    return Panel(child=layout, title='Peta Kasus Harian COVID-19 Indonesia')
