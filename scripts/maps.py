import json

# Mengimport modul widget, layout, model dan plotting pada bokeh
from bokeh.models import (ColumnDataSource, CategoricalColorMapper, Panel,
                          GeoJSONDataSource, ColorBar, TableColumn, HoverTool, Slider)


from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import Button, DataTable
from bokeh.layouts import row, WidgetBox


def maps_covid(covid19, indonesia):
    # Mengkategorikan Jumlah Kasus COVID-19 untuk acuan heatmap wilayah
    def category_covid(df):
        if df == 0:
            category = '0'
        elif 1 <= df <= 19:
            category = '1 - 19'
        elif 20 <= df <= 99:
            category = '20 - 99'
        elif 100 <= df <= 999:
            category = '100 - 999'
        elif 1000 <= df <= 3999:
            category = '1000 - 3999'
        elif 4000 <= df <= 6999:
            category = '4000 - 6999'
        elif 7000 <= df <= 9999:
            category = '7000 - 9999'
        elif 10000 <= df <= 999999:
            category = '10000 - 999999'

        return category

    # Menghitung jumlah hari sejak tanggal awal pada dataset
    def map_date():
        date_to_day = {}
        date = covid19['tanggal'].unique()

        for j, val in enumerate(date):
            date_to_day[val] = j + 1

        return date_to_day

    # Merubah format dataset menjadi json untuk visualisasi geospasial
    def json_data(selected_day):
        # Seleksi data berdasarkan hari yang dipilih
        df_dt = covid19.loc[covid19['day'] == selected_day]
        df_dt = df_dt.fillna(0)

        # Merge dataset GeoDataframe object dengan data covid19
        merge = indonesia.merge(df_dt, how='left', left_on=['PROVINSI'], right_on=['PROVINSI'])
        merge['PROVINSI'] = merge['PROVINSI'].str.title()

        # Convert dataset ke tipe json
        merge_json = json.loads(merge.to_json())

        # Convert dataset json ke tipe object
        json_data_new = json.dumps(merge_json)

        return json_data_new

    # Fungsi untuk membuat ranking kasus covid dan dataset pada tabel
    def column_data(selected_day):
        # Seleksi data berdasarkan hari yang dipilih
        column = covid19.loc[covid19['day'] == selected_day]

        # Melakukan sorting rangking berdasarkan kasus tiap provinsi
        column = column.sort_values(by='KASUS', ascending=False)

        # Melakukan perhitungan untuk index rangking setiap provinsi
        rank = []
        for counter in range(column.index.shape[0]):
            rank.append(counter + 1)

        column['rank'] = rank

        # Mengambil 20 Data Teratas
        most_confirmed = column.head(20)
        most_confirmed['PROVINSI'] = most_confirmed['PROVINSI'].str.title()

        # Membuat source dataset baru untuk tabel ranking kasus
        new_source = dict(
            rank=[rank for rank in most_confirmed['rank']],
            provinsi=[country for country in most_confirmed['PROVINSI']],
            confirmed=[confirmed for confirmed in most_confirmed['KASUS']],
            tanggal=[tanggal for tanggal in most_confirmed['tanggal']],
        )

        return new_source

    # Mengupdate plot ketika widget digunakan oleh user
    def update_plot(attr, old, new):
        day = slider.value
        new_data = json_data(day)
        geosource.geojson = new_data
        source.data = column_data(day)

    # Mengupdate value perhitungan tanggal
    def animate_update():
        val = slider.value + 1
        if val > 365:
            val = 0

        slider.value = val

    # Kontrol animasi pada plot dan tabel
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

    # Membuat list yang berisi warna untuk heatmap
    list_category = [
        '0', '1 - 19', '20 - 99', '100 - 999', '1000 - 3999',
        '4000 - 6999', '7000 - 9999', '10000 - 99999'
    ]

    # Membuat list yang berisi warna untuk heatmap
    palet = ['#67000d', '#cb181d', '#ef3b2c', '#fc9272', '#fcbba1', '#f7dada', '#fcf2f2', '#ffffff']
    palet = palet[::-1]

    # Menggunakan kategorikal color mapper sebagai pewarnaan heatmap tiap provinsi
    color_mapper = CategoricalColorMapper(factors=list_category, palette=palet)

    # Menampilkan legend untuk categorical mapper
    color_bar = ColorBar(
        color_mapper=color_mapper,
        title_text_font_style='bold',
        title_text_font_size='12px',
        title_text_align='center',
        orientation='vertical',
        major_label_text_font_size='12px',
        major_label_text_font_style='bold',
    )

    # Membuat tampilan untuk slider
    slider = Slider(title='Hari Ke', start=1, end=365, step=1, value=1)

    # Mengganti value pada DataSource ketika pengguna menggunakan slider
    slider.on_change('value', update_plot)

    # Inisialisasi objek figure untuk dan melakukan styling pada visualisasi plot
    r = figure(title="", plot_height=500, plot_width=1000, toolbar_location='below', tools=['pan, wheel_zoom, reset'])
    r.title.align = 'center'
    r.xaxis.visible = False
    r.yaxis.visible = False
    r.xgrid.grid_line_color = None
    r.ygrid.grid_line_color = None

    # Menambahkan potongan setiap wilayah indonesia kedalam plot
    states = r.patches(
        'xs', 'ys', source=geosource,
        fill_color={'field': 'category', 'transform': color_mapper},
        line_color='gray',
        line_width=0.25,
        fill_alpha=1,
    )

    # Menambahkan layout untuk legend heatmap
    r.add_layout(color_bar)

    # Membuat hover pada visualisasi plot geospasial
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

    # Membuat tombol animasi
    callback_id = None
    button = Button(label='► Play', width=60)
    button.on_click(animate)

    # Membuat column untuk tabel rangking kasus
    columns = [
        TableColumn(field='rank', title='Peringkat Kasus'),
        TableColumn(field='provinsi', title='Provinsi'),
        TableColumn(field='confirmed', title='Terkonfirmasi'),
    ]

    # Membuat plot untuk tabel
    tabel = DataTable(
        source=source, columns=columns, width=500,
        height=600, index_position=None
    )

    # Membuat layout untuk setiap widget dan plot yang telah dibuat
    layout = row(WidgetBox(slider, tabel, button), r)
    tab = Panel(child=layout, title='Peta Kasus Harian COVID-19 Indonesia')

    return tab
