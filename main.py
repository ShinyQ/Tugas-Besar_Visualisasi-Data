# Mengimport Library Pandas Untuk Manipulasi Dataframe
# Dan Geopandas Untuk Manipulasi Tipe Dataset Geospatial
import pandas as pd
import geopandas as gpd

# Mengimport fungsi untuk memanipulasi path dataset yang akan diambil
from os.path import dirname, join

# Mengimport library bokeh
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Mengimport tab yang telah dibuat
from scripts.lineplot import lineplot_visualization
from scripts.maps import maps_covid

# Membaca dataset COVID-19 untuk setiap wilayah Indonesia
covid19 = pd.read_csv(join(dirname(__file__), 'data', 'prov_case.csv'))

# Membaca dataset geospatial wilayah Indonesia
indonesia = gpd.read_file(join(dirname(__file__), 'data/geoindo', 'Batas Provinsi.shp'))

# Membuat tab untuk setiap menu visualisasi
tab1 = lineplot_visualization(covid19)
tab2 = maps_covid(covid19, indonesia)

# Menggabungkan seluruh navigasi kedalam tab navigasi
tabs = Tabs(tabs=[tab1, tab2])

# Menampilkan seluruh tab pada dokumen utama situs
curdoc().add_root(tabs)
curdoc().title = "Kasus COVID-19 Indonesia"
