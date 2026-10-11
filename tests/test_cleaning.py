"""The cleaning step, on a hand-built frame: no data file, no network.

One rule per test, each one a figure that was wrong before: a zero surface
produced an infinite price per square metre, which then led every outlier chart.
"""

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning import dataframe_cleaner  # noqa: E402


def _raw(**overrides):
    base = {
        "postcode": [1000, 4000, 4000],
        "price": [300000.0, 200000.0, 200000.0],
        "livable_surface": [100.0, 0.0, None],
        "address": ["Rue A 1", "Rue B 2", "Rue C 3"],
        "build_year": [1990.0, None, 2000.0],
        "bedroom_count": [2.0, 3.0, 1.0],
        "total_surface": [120.0, 80.0, 60.0],
        "garage": [1.0, None, None],
        "terrace": [1.0, 0.0, 1.0],
        "swimming_pool": [None, None, 1.0],
        "peb_category": [150.0, 200.0, 250.0],
        "Preschool_distance": [300.0, 500.0, 700.0],
        "Train_station_distance": [1000.0, 2000.0, 3000.0],
        "Supermarket_distance": [200.0, 400.0, 600.0],
        "distance_nearest_city": [1.0, 2.0, 3.0],
        "city": ["Bruxelles", "Li&egrave;ge", "Liège"],
        "province": ["Brussels", "Liège", "Liège"],
        "nearest_city": ["Bruxelles", "Liège", "Liège"],
        "property_state": ["Good", "To be renovated", "New"],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_a_zero_or_missing_surface_gives_no_price_per_m2_rather_than_infinity(tmp_path):
    clean = dataframe_cleaner(_raw(), tmp_path / "clean.json")
    per_m2 = clean["price_per_m2"].tolist()
    assert per_m2[0] == 3000.0
    assert all(math.isnan(v) for v in per_m2[1:]), per_m2
    assert not any(math.isinf(v) for v in per_m2)


def test_html_entities_are_unescaped_and_the_state_label_is_unified(tmp_path):
    clean = dataframe_cleaner(_raw(), tmp_path / "clean.json")
    assert clean["city"].tolist()[1] == "Liège"
    assert "To be renovated" not in clean["property_state"].tolist()


def test_silence_about_a_garage_is_imputed_as_none(tmp_path):
    """The imputation the module documents: a listing that says nothing has 0."""
    clean = dataframe_cleaner(_raw(), tmp_path / "clean.json")
    assert clean["garage"].tolist() == [1, 0, 0]
    assert clean["swimming_pool"].tolist() == [0, 0, 1]


def test_the_cleaned_frame_is_written_where_asked(tmp_path):
    target = tmp_path / "out" / "clean.json"
    target.parent.mkdir()
    dataframe_cleaner(_raw(), target)
    assert len(pd.read_json(target)) == 3
