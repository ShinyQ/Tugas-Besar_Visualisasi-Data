# Mengimport modul widget, layout dan plotting pada bokeh
from bokeh.models import HoverTool, ColumnDataSource, Panel, Select, DateRangeSlider, Legend
from bokeh.plotting import figure
from bokeh.layouts import column, row

# Mengimport modul manipulasi tanggal menggunakan datetime dan pandas
from pandas import to_datetime
from datetime import date


def lineplot_visualization(df):
    # Mengcopy dataset sehingga dataset utama tidak berubah
    dataset = df.copy()

    # Merubah format tanggal ke datetime
    dataset["tanggal"] = to_datetime(dataset["tanggal"])

    # Fungsi untuk membuat data source baru
    def make_dataset(data):
        return ColumnDataSource(data)

    # Fungsi untuk melakukan style pada plot visualisasi
    def style(plot):
        plot.title.align = "center"
        plot.title.text_font_size = "20pt"
        plot.xaxis.axis_label_text_font_size = "14pt"
        plot.xaxis.axis_label_text_font_style = "bold"
        plot.yaxis.axis_label_text_font_size = "14pt"
        plot.yaxis.axis_label_text_font_style = "bold"
        plot.xaxis.major_label_text_font_size = "12pt"
        plot.yaxis.major_label_text_font_size = "12pt"

        return plot

    # Fungsi untuk melakukan plotting terhadap kasus covid-19 melalui lineplot
    def case_plot(data):
        # Inisialisasi plot
        figur = figure(
            plot_width=1200,
            plot_height=500,
            title="Pertumbuhan Kasus Covid-19",
            x_axis_label="Tanggal",
            y_axis_label="Data",
            x_axis_type="datetime",
        )

        # Inisialisasi hover pada plot
        hover = HoverTool(
            tooltips=[
                ("Tanggal", "@tanggal{%F}"),
                ("Kasus", "@KASUS"),
                ("Sembuh", "@SEMBUH"),
                ("Meninggal", "@MENINGGAL"),
                ("Dirawat/Isolasi", "@DIRAWAT_OR_ISOLASI"),
                ("Akumulasi Kasus", "@AKUMULASI_KASUS"),
                ("Akumulasi Sembuh", "@AKUMULASI_SEMBUH"),
                ("Akumulasi Meninggal", "@AKUMULASI_MENINGGAL"),
                ("Akumulasi Dirawat/Isolasi", "@AKUMULASI_DIRAWAT_OR_ISOLASI"),
            ],

            formatters={"@tanggal": "datetime"},
        )

        # Membuat line dan circle pada plot untuk kasus terkonfirmasi covid
        kasus = figur.line("tanggal", "KASUS", source=data, color="red")
        figur.circle(
            "tanggal", "KASUS", source=data,
            fill_alpha=0.7,
            hover_fill_color="purple",
            hover_fill_alpha=1,
            color="red",
            size=3,
        )

        # Membuat line dan circle pada plot untuk kasus sembuh covid
        sembuh = figur.line("tanggal", "SEMBUH", source=data, color="green")
        figur.circle(
            "tanggal", "SEMBUH", source=data,
            fill_alpha=0.7,
            hover_fill_color="purple",
            hover_fill_alpha=1,
            color="green",
            size=3,
        )

        # Menambahkan legend untuk kedua lineplot kasus covid
        legend = Legend(items=[("Terkonfirmasi", [kasus]), ("Sembuh", [sembuh])], orientation="horizontal")

        # Menambahkan hover pada plot dan melakukan styling plot
        figur.add_layout(legend)
        figur.legend.location = "top_left"
        figur.add_tools(hover)
        figur = style(figur)

        return figur

    # Fungsi callback yang mengupdate dataset berdasarkan provinsi dan range tanggal
    def update(attr, old, new):
        new_dataset = dataset.loc[
            (dataset["PROVINSI"] == menu.value.upper()) &
            (dataset["tanggal"].between(
                to_datetime(tanggal.value_as_date[0]),
                to_datetime(tanggal.value_as_date[1])
            ))
        ]

        # Mengupdate dataset baru sesuai kriteria
        new_src = make_dataset(new_dataset)
        src.data.update(new_src.data)

        return menu.value

    # Mendefinisikan list provinsi dan melakukan sorting secara ascending
    option = list(dataset["PROVINSI"].value_counts().index)
    option = [x.title() for x in option]
    option.sort()

    # Membuat menu untuk pemilihan provinsi yang diinginkan
    menu = Select(options=option, value="ACEH", title="Provinsi")

    # Membuat slider tanggal untuk pemilihan jarak tanggal yang diinginkan
    tanggal = DateRangeSlider(
        value=(date(2021, 1, 1), date(2022, 1, 1)),
        start=date(2021, 1, 1), end=date(2022, 1, 1),
    )

    # Mengupdate value jika pengguna merubah pilihan
    menu.on_change("value", update)
    tanggal.on_change("value", update)

    # Inisialisasi dataset untuk visualisasi awal pada tampilan plot
    dataset1 = dataset[dataset["PROVINSI"] == menu.value.upper()]
    src = make_dataset(dataset1)

    # Menyusun widget dan layout plot visualisasi
    layout1 = row([column(menu, tanggal)])
    layout2 = column([case_plot(src)])
    layout = row(layout1, layout2)

    tab = Panel(child=layout, title="Lineplot Kasus COVID-19 Indonesia")

    return tab
