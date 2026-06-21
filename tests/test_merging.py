import pandas as pd
from app.merging import _rename_with_wave_suffix, merge_wide, merge_long


def test_rename_with_wave_suffix():
    df = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    result = _rename_with_wave_suffix(df, "_w1", "id")
    assert list(result.columns) == ["id", "val_w1"]
    assert result["id"].tolist() == [1, 2]


def test_rename_with_wave_suffix_preserves_primary_key():
    df = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    result = _rename_with_wave_suffix(df, "_w2", "id")
    assert "id" in result.columns
    assert result["id"].tolist() == [1, 2]


def test_merge_wide_inner(df1, df2):
    assignments = {1: 1, 2: 2}
    result = merge_wide([df1, df2], "id", "inner", assignments)
    assert result.shape[0] == 3
    assert "name_w1" in result.columns
    assert "name_w2" in result.columns
    assert "score_w1" in result.columns
    assert "score_w2" in result.columns


def test_merge_wide_left_only_in_first():
    df_a = pd.DataFrame({"id": [1, 2, 3], "x": [10, 20, 30]})
    df_b = pd.DataFrame({"id": [1, 2], "y": [100, 200]})
    assignments = {1: 1, 2: 2}
    result = merge_wide([df_a, df_b], "id", "left", assignments)
    assert result.shape[0] == 3
    assert result["y_w2"].isna().sum() == 1


def test_merge_wide_outer():
    df_a = pd.DataFrame({"id": [1, 2], "x": [10, 20]})
    df_b = pd.DataFrame({"id": [2, 3], "y": [200, 300]})
    assignments = {1: 1, 2: 2}
    result = merge_wide([df_a, df_b], "id", "outer", assignments)
    assert result.shape[0] == 3
    assert result["id"].tolist() == [1, 2, 3]


def test_merge_wide_right():
    df_a = pd.DataFrame({"id": [1, 2], "x": [10, 20]})
    df_b = pd.DataFrame({"id": [2, 3], "y": [200, 300]})
    assignments = {1: 1, 2: 2}
    result = merge_wide([df_a, df_b], "id", "right", assignments)
    assert result.shape[0] == 2
    assert result["id"].tolist() == [2, 3]


def test_merge_long_basic(df1, df2):
    assignments = {1: 1, 2: 2}
    result, common_count = merge_long([df1, df2], "id", assignments)
    assert common_count == 3
    assert result.shape[0] == 6
    assert "Wave" in result.columns
    assert result["Wave"].tolist() == ["w1", "w1", "w1", "w2", "w2", "w2"]


def test_merge_long_filters_common_ids():
    df_a = pd.DataFrame({"id": [1, 2, 3], "x": [10, 20, 30]})
    df_b = pd.DataFrame({"id": [2, 3, 4], "y": [200, 300, 400]})
    assignments = {1: 1, 2: 2}
    result, common_count = merge_long([df_a, df_b], "id", assignments)
    assert common_count == 2
    assert result["id"].unique().tolist() == [2, 3]


def test_merge_long_does_not_mutate_input(df1, df2):
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    assignments = {1: 1, 2: 2}
    merge_long([df1, df2], "id", assignments)
    assert df1.equals(df1_copy)
    assert df2.equals(df2_copy)


def test_rename_does_not_mutate_input():
    df = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df_copy = df.copy()
    _rename_with_wave_suffix(df, "_w1", "id")
    assert df.equals(df_copy)
