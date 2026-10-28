"""Chart specs requested from the LLM.

The model returns a ChartSpec (structured output), never code. The app validates the
spec against the dataframe, builds the figure itself, and generates the Python/R code
shown to the user from the same spec. Nothing the model returns is executed.
"""
import json
import re
from typing import Literal, Optional

import pandas as pd
import plotly.express as px
from pydantic import BaseModel, Field

ChartType = Literal["line", "scatter", "bar", "histogram", "box", "area"]
Aggregate = Literal["mean", "sum", "min", "max", "count"]

PX_FUNCTIONS = {
    "line": px.line,
    "scatter": px.scatter,
    "bar": px.bar,
    "histogram": px.histogram,
    "box": px.box,
    "area": px.area,
}

# plot_ly trace arguments per chart type
R_TRACES = {
    "line": 'type = "scatter", mode = "lines"',
    "scatter": 'type = "scatter", mode = "markers"',
    "bar": 'type = "bar"',
    "histogram": 'type = "histogram"',
    "box": 'type = "box"',
    "area": 'type = "scatter", mode = "lines", fill = "tozeroy"',
}

MAX_TITLE_LENGTH = 120


class ChartSpecError(ValueError):
    """The spec can't be drawn from this dataframe."""


class ChartFilter(BaseModel):
    column: str = Field(description="Column to filter on.")
    values: list[str] = Field(description="Keep rows whose column value is one of these.")


class ChartSpec(BaseModel):
    """A Plotly chart of the air quality dataframe."""

    chart_type: ChartType = Field(description="Kind of chart.")
    x: str = Field(description="Column for the x axis.")
    y: Optional[str] = Field(default=None, description="Column for the y axis. Optional for histogram and count.")
    color: Optional[str] = Field(default=None, description="Column that splits the data into colored series.")
    aggregate: Optional[Aggregate] = Field(
        default=None, description="Aggregate y for each x (and color) group. 'count' counts rows."
    )
    filters: list[ChartFilter] = Field(default_factory=list, description="Row filters applied before plotting.")
    title: str = Field(default="", description="Chart title.")


def describe_dataframe(df, max_values=25):
    """Column names, dtypes and (for text columns) allowed values, for the LLM prompt."""
    lines = []
    for col in df.columns:
        line = f"- {col} ({df[col].dtype})"
        if df[col].dtype == object:
            values = sorted(df[col].dropna().unique())
            if len(values) <= max_values:
                line += ": " + ", ".join(json.dumps(v) for v in values)
        lines.append(line)
    return "\n".join(lines)


def clean_title(title):
    # Plotly renders some HTML in titles, and backticks would break the code fence.
    return re.sub(r"[<>`]", "", title or "").strip()[:MAX_TITLE_LENGTH]


def validate_spec(spec, df):
    columns = set(df.columns)
    for name in ("x", "y", "color"):
        value = getattr(spec, name)
        if value is not None and value not in columns:
            raise ChartSpecError(f"Unknown column '{value}' for {name}.")
    for f in spec.filters:
        if f.column not in columns:
            raise ChartSpecError(f"Unknown filter column '{f.column}'.")
        if not f.values:
            raise ChartSpecError(f"Filter on '{f.column}' has no values.")
        filter_values(f, df)
    needs_y = spec.chart_type != "histogram" and spec.aggregate != "count"
    if needs_y and spec.y is None:
        raise ChartSpecError(f"A {spec.chart_type} chart needs a y column.")
    if spec.aggregate not in (None, "count") and not pd.api.types.is_numeric_dtype(df[spec.y]):
        raise ChartSpecError(f"Can't take the {spec.aggregate} of non-numeric column '{spec.y}'.")


def filter_values(f, df):
    """Filter values come back as strings; convert them to the column's type."""
    if pd.api.types.is_numeric_dtype(df[f.column]):
        try:
            return [pd.to_numeric(v).item() for v in f.values]
        except (ValueError, TypeError):
            raise ChartSpecError(f"Filter on numeric column '{f.column}' has non-numeric values.")
    return list(f.values)


def _group_cols(spec):
    return [spec.x] + ([spec.color] if spec.color and spec.color != spec.x else [])


def _y_col(spec):
    return "count" if spec.aggregate == "count" else spec.y


def prepare_data(spec, df):
    data = df
    for f in spec.filters:
        data = data[data[f.column].isin(filter_values(f, df))]
    if data.empty:
        raise ChartSpecError("No rows match the filters.")
    if spec.aggregate == "count":
        data = data.groupby(_group_cols(spec), as_index=False).size().rename(columns={"size": "count"})
    elif spec.aggregate:
        data = data.groupby(_group_cols(spec), as_index=False)[spec.y].agg(spec.aggregate)
    return data


def build_figure(spec, df):
    validate_spec(spec, df)
    data = prepare_data(spec, df)
    kwargs = {"x": spec.x, "title": clean_title(spec.title)}
    if _y_col(spec):
        kwargs["y"] = _y_col(spec)
    if spec.color:
        kwargs["color"] = spec.color
    return PX_FUNCTIONS[spec.chart_type](data, **kwargs)


def to_python_code(spec, df, df_name="cleaned_df"):
    lines = ["import plotly.express as px", "", f"data = {df_name}"]
    for f in spec.filters:
        lines.append(f"data = data[data[{f.column!r}].isin({filter_values(f, df)!r})]")
    if spec.aggregate == "count":
        lines.append(
            f'data = data.groupby({_group_cols(spec)!r}, as_index=False).size().rename(columns={{"size": "count"}})'
        )
    elif spec.aggregate:
        lines.append(f"data = data.groupby({_group_cols(spec)!r}, as_index=False)[{spec.y!r}].agg({spec.aggregate!r})")
    args = [f"x={spec.x!r}"]
    if _y_col(spec):
        args.append(f"y={_y_col(spec)!r}")
    if spec.color:
        args.append(f"color={spec.color!r}")
    args.append(f"title={clean_title(spec.title)!r}")
    lines += [f"fig = px.{spec.chart_type}(data, {', '.join(args)})", "fig.show()"]
    return "\n".join(lines)


def to_r_code(spec, df, df_name="cleaned_df"):
    steps = [df_name]
    for f in spec.filters:
        values = ", ".join(json.dumps(v) for v in filter_values(f, df))
        steps.append(f"filter({f.column} %in% c({values}))")
    if spec.aggregate:
        steps.append(f"group_by({', '.join(_group_cols(spec))})")
        if spec.aggregate == "count":
            steps.append('summarise(count = n(), .groups = "drop")')
        else:
            steps.append(f'summarise({spec.y} = {spec.aggregate}({spec.y}, na.rm = TRUE), .groups = "drop")')
    args = [f"x = ~{spec.x}"]
    if _y_col(spec):
        args.append(f"y = ~{_y_col(spec)}")
    if spec.color:
        args.append(f"color = ~{spec.color}")
    args.append(R_TRACES[spec.chart_type])
    lines = ["library(dplyr)", "library(plotly)", "", "data <- " + " %>%\n  ".join(steps), ""]
    lines.append(f"plot_ly(data, {', '.join(args)}) %>%")
    lines.append(f"  layout(title = {json.dumps(clean_title(spec.title))})")
    return "\n".join(lines)
