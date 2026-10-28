import pandas as pd
import pytest

from chart_spec import (
    ChartFilter,
    ChartSpec,
    ChartSpecError,
    build_figure,
    clean_title,
    to_python_code,
    to_r_code,
)

DF = pd.DataFrame(
    {
        "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-04-01", "2024-04-01"]),
        "county": ["Los Angeles", "San Diego", "Los Angeles", "San Diego"],
        "year": [2024, 2024, 2024, 2024],
        "arithmetic_mean": [1.0, 2.0, 3.0, 4.0],
    }
)

SPECS = [
    ChartSpec(chart_type="line", x="date", y="arithmetic_mean", color="county", title="Lead"),
    ChartSpec(chart_type="bar", x="county", y="arithmetic_mean", aggregate="mean"),
    ChartSpec(chart_type="bar", x="county", aggregate="count"),
    ChartSpec(chart_type="histogram", x="arithmetic_mean"),
    ChartSpec(
        chart_type="scatter",
        x="date",
        y="arithmetic_mean",
        filters=[ChartFilter(column="county", values=["San Diego"])],
    ),
]


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: f"{s.chart_type}-{s.aggregate}")
def test_generated_python_code_draws_the_same_figure(spec):
    # Running our own generated code (never model output) keeps the shown code honest.
    scope = {"cleaned_df": DF}
    exec(to_python_code(spec, DF).replace("fig.show()", ""), scope)
    assert scope["fig"].to_json() == build_figure(spec, DF).to_json()


def test_aggregate_mean_groups_by_x():
    fig = build_figure(SPECS[1], DF)
    assert list(fig.data[0].y) == [2.0, 3.0]


def test_count_needs_no_y():
    fig = build_figure(SPECS[2], DF)
    assert list(fig.data[0].y) == [2, 2]


def test_filter_keeps_matching_rows():
    fig = build_figure(SPECS[4], DF)
    assert list(fig.data[0].y) == [2.0, 4.0]


@pytest.mark.parametrize(
    "spec, message",
    [
        (ChartSpec(chart_type="line", x="nope", y="arithmetic_mean"), "Unknown column 'nope'"),
        (ChartSpec(chart_type="line", x="date"), "needs a y column"),
        (ChartSpec(chart_type="bar", x="date", y="county", aggregate="mean"), "non-numeric"),
        (
            ChartSpec(
                chart_type="line", x="date", y="arithmetic_mean", filters=[ChartFilter(column="x2", values=["1"])]
            ),
            "Unknown filter column",
        ),
        (
            ChartSpec(
                chart_type="line",
                x="date",
                y="arithmetic_mean",
                filters=[ChartFilter(column="county", values=["Kern"])],
            ),
            "No rows match",
        ),
    ],
)
def test_invalid_specs_raise(spec, message):
    with pytest.raises(ChartSpecError, match=message):
        build_figure(spec, DF)


def test_numeric_filter_values_are_converted():
    spec = ChartSpec(
        chart_type="line", x="date", y="arithmetic_mean", filters=[ChartFilter(column="year", values=["2024"])]
    )
    assert len(build_figure(spec, DF).data[0].x) == 4
    assert ".isin([2024])" in to_python_code(spec, DF)
    bad = spec.model_copy(update={"filters": [ChartFilter(column="year", values=["last year"])]})
    with pytest.raises(ChartSpecError, match="non-numeric values"):
        build_figure(bad, DF)


def test_title_is_cleaned():
    assert clean_title("<a href='x'>Lead</a> ```") == "a href='x'Lead/a"
    assert len(clean_title("x" * 500)) == 120


def test_r_code():
    spec = ChartSpec(
        chart_type="area",
        x="date",
        y="arithmetic_mean",
        color="county",
        aggregate="max",
        filters=[ChartFilter(column="county", values=["Los Angeles"])],
        title='Say "hi"',
    )
    assert to_r_code(spec, DF) == (
        "library(dplyr)\n"
        "library(plotly)\n\n"
        "data <- cleaned_df %>%\n"
        '  filter(county %in% c("Los Angeles")) %>%\n'
        "  group_by(date, county) %>%\n"
        '  summarise(arithmetic_mean = max(arithmetic_mean, na.rm = TRUE), .groups = "drop")\n\n'
        "plot_ly(data, x = ~date, y = ~arithmetic_mean, color = ~county, "
        'type = "scatter", mode = "lines", fill = "tozeroy") %>%\n'
        '  layout(title = "Say \\"hi\\"")'
    )
