import pandas as pd
import pytest


@pytest.fixture
def df1():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["A", "B", "C"],
        "score": [10, 20, 30],
    })


@pytest.fixture
def df2():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["A", "B", "C"],
        "score": [15, 25, 35],
    })


@pytest.fixture
def df_with_duplicates():
    return pd.DataFrame({
        "id": [1, 1, 2, 3],
        "name": ["A", "A", "B", "C"],
        "score": [10, 10, 20, 30],
    })


@pytest.fixture
def df_with_missing():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "score": [10, None, 30],
        "value": [None, "B", None],
    })
