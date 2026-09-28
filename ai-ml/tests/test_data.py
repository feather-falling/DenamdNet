import pytest
import sys, os
sys.path.insert(0, os.path.abspath("ai-ml"))

from preprocessing.load_data import DataLoader
from preprocessing.validate_data import DataValidator

def test_data_loader_and_validator():
    loader = DataLoader(base_dir="data")
    cdata = loader.load_country_data("india")

    assert "demand" in cdata
    assert "inventory" in cdata

    meds = cdata["medicines"]["medicines"] if isinstance(cdata["medicines"], dict) and "medicines" in cdata["medicines"] else cdata["medicines"]
    phcs = cdata["phcs"]["phcs"] if isinstance(cdata["phcs"], dict) and "phcs" in cdata["phcs"] else cdata["phcs"]

    assert len(meds) >= 10
    assert len(phcs) >= 10

    validator = DataValidator()
    is_valid, errors = validator.validate(cdata)
    assert is_valid, f"Validation errors: {errors}"
