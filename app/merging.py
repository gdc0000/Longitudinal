from functools import reduce

import pandas as pd

from app.config import WAVE_COL


def _rename_with_wave_suffix(
    df: pd.DataFrame, suffix: str, primary_key: str
) -> pd.DataFrame:
    renamed = df.copy()
    new_columns = {
        col: f"{col}{suffix}" if col != primary_key else col
        for col in renamed.columns
    }
    renamed.rename(columns=new_columns, inplace=True)
    return renamed


def merge_wide(
    dataframes: list[pd.DataFrame],
    primary_key: str,
    join_type: str,
    wave_assignments: dict[int, int],
) -> pd.DataFrame:
    renamed = [
        _rename_with_wave_suffix(df, f"_w{wave_assignments[i]}", primary_key)
        for i, df in enumerate(dataframes, start=1)
    ]
    return reduce(
        lambda left, right: pd.merge(left, right, on=primary_key, how=join_type),
        renamed,
    )


def merge_long(
    dataframes: list[pd.DataFrame],
    primary_key: str,
    wave_assignments: dict[int, int],
) -> tuple[pd.DataFrame, int]:
    copies = [df.copy() for df in dataframes]

    for i, df in enumerate(copies, start=1):
        df[WAVE_COL] = f"w{wave_assignments[i]}"

    concatenated = pd.concat(copies, ignore_index=True)

    common_ids = set.intersection(
        *(set(df[primary_key]) for df in copies)
    )

    result = concatenated[concatenated[primary_key].isin(common_ids)]
    return result, len(common_ids)
