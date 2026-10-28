import importlib.util
import json
import os
from pathlib import Path

import pandas as pd
import pytest
import sqlalchemy
from langchain_core.language_models import FakeListChatModel
from langchain_core.runnables import RunnableLambda

PYTHON_DIR = Path(__file__).resolve().parents[1]


class FakeChartModel(FakeListChatModel):
    """Fake chat model that also supports with_structured_output by parsing its reply as JSON."""

    def with_structured_output(self, schema, **kwargs):
        return self | RunnableLambda(lambda msg: schema.model_validate(json.loads(msg.content)))


@pytest.fixture(scope="module")
def dash_app(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    pd.read_csv(PYTHON_DIR / "data/combined_data_20251006.csv").to_sql(
        "air_quality", engine, index=False
    )
    env = {"DB_CONNECTION_TYPE": "sqlite", "GEMINI_API_KEY": "fake", "SQLITE_DB_PATH": str(db_path)}
    old_env = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    old_cwd = os.getcwd()
    os.chdir(PYTHON_DIR)
    try:
        spec = importlib.util.spec_from_file_location("dash_app", PYTHON_DIR / "dash-app.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        os.chdir(old_cwd)
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_llm_output_is_never_executed(dash_app, tmp_path):
    marker = tmp_path / "executed"
    reply = f"```python\nopen({str(marker)!r}, 'w').close()\nfig = None\n```"
    dash_app.llm = FakeChartModel(responses=[reply])

    dash_app.create_graph(1, "Show lead levels over time", "Python")

    assert not marker.exists(), "model output was executed as code"


@pytest.mark.parametrize("language", ["Python", "R"])
def test_chart_spec_renders_figure_and_code(dash_app, language):
    spec = {
        "chart_type": "line",
        "x": "date",
        "y": "arithmetic_mean",
        "color": "county",
        "aggregate": "mean",
        "filters": [{"column": "county", "values": ["Los Angeles", "San Diego"]}],
        "title": "Lead by county",
    }
    dash_app.llm = FakeChartModel(responses=[json.dumps(spec)])

    graph, title, code = dash_app.create_graph(1, "Line chart of lead by county", language)

    assert graph.figure is not None
    assert {trace.name for trace in graph.figure.data} == {"Los Angeles", "San Diego"}
    assert language in title
    assert ("plot_ly(" if language == "R" else "px.line(") in code


def test_invalid_spec_returns_message(dash_app):
    dash_app.llm = FakeChartModel(responses=[json.dumps({"chart_type": "line", "x": "not_a_column"})])

    graph, title, code = dash_app.create_graph(1, "Plot something", "Python")

    assert "not_a_column" in str(graph.children)
    assert code == ""
