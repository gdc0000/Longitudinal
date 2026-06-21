import pandas as pd
from app.processing import remove_duplicates, fill_missing_values


def test_remove_duplicates_removes_duplicates(df_with_duplicates):
    result = remove_duplicates([df_with_duplicates], "id")
    assert len(result[0]) == 3
    assert result[0]["id"].is_unique


def test_remove_duplicates_unchanged_without_duplicates(df1):
    result = remove_duplicates([df1], "id")
    assert len(result[0]) == 3
    assert result[0].equals(df1)


def test_remove_duplicates_no_primary_key(df_with_duplicates):
    result = remove_duplicates([df_with_duplicates], "")
    assert len(result[0]) == 4
    assert result[0].equals(df_with_duplicates)


def test_remove_duplicates_primary_key_not_in_columns(df_with_duplicates):
    result = remove_duplicates([df_with_duplicates], "nonexistent")
    assert len(result[0]) == 4
    assert result[0].equals(df_with_duplicates)


def test_remove_duplicates_multiple_dataframes(df1, df_with_duplicates):
    result = remove_duplicates([df1, df_with_duplicates], "id")
    assert len(result[0]) == 3
    assert len(result[1]) == 3
    assert result[1]["id"].is_unique


def test_fill_missing_values_default(df_with_missing):
    result = fill_missing_values([df_with_missing], 0)
    assert result[0].iloc[1]["score"] == 0
    assert result[0].iloc[0]["value"] == 0
    assert result[0].iloc[2]["value"] == 0


def test_fill_missing_values_string(df_with_missing):
    result = fill_missing_values([df_with_missing], "Unknown")
    assert result[0].iloc[1]["score"] == "Unknown"
    assert result[0].iloc[0]["value"] == "Unknown"


def test_fill_missing_values_multiple_dataframes(df_with_missing, df1):
    result = fill_missing_values([df_with_missing, df1], 0)
    assert len(result) == 2
    assert result[1].equals(df1)
