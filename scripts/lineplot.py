from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Panel, Select, DateRangeSlider
from bokeh.layouts import column, row
from pandas import to_datetime
from datetime import date


def lineplot_visualization(dataset):
    dataset = dataset.copy()
    dataset["tanggal"] = to_datetime(dataset["tanggal"])

    def make_dataset(data):
        return ColumnDataSource(data)

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

    def case_plot(data):
        figur = figure(
            plot_width=1200,
            plot_height=600,
            title="Pertumbuhan Kasus Covid-19",
            x_axis_label="Tanggal",
            y_axis_label="Data",
            x_axis_type="datetime",
        )

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

        figur.line("tanggal", "KASUS", source=data, color="gray")
        figur.circle(
            "tanggal", "KASUS", source=data,
            fill_alpha=0.7,
            hover_fill_color="purple",
            hover_fill_alpha=1,
            color="red",
            size=3,
        )

        figur.add_tools(hover)
        figur = style(figur)
        return figur

    def update(attr, old, new):
        new_dataset = dataset.loc[
            (dataset["PROVINSI"] == menu.value.upper()) &
            (dataset["tanggal"].between(
                to_datetime(tanggal.value_as_date[0]),
                to_datetime(tanggal.value_as_date[1])
            ))
        ]

        new_src = make_dataset(new_dataset)
        src.data.update(new_src.data)

        return menu.value

    option = list(dataset["PROVINSI"].value_counts().index)
    option = [x.title() for x in option]
    option.sort()

    menu = Select(options=option, value="ACEH", title="Provinsi")
    menu.on_change("value", update)

    tanggal = DateRangeSlider(
        value=(date(2021, 1, 1), date(2022, 1, 1)),
        start=date(2021, 1, 1), end=date(2022, 1, 1),
    )

    tanggal.on_change("value", update)

    dataset1 = dataset[dataset["PROVINSI"] == menu.value.upper()]
    src = make_dataset(dataset1)

    layout1 = row([column(menu, tanggal)])
    layout2 = column([case_plot(src)])
    layout = row(layout1, layout2)

    tab = Panel(child=layout, title="Lineplot Kasus COVID-19 Indonesia")

    return tab
