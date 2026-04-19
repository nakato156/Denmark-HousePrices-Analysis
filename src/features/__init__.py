# src/features/__init__.py
"""
Módulo de features modularizado para feature engineering.
"""
from .data_cleaning import (
    filter_regular_sales,
    handle_missing_values,
    remove_price_outliers,
    calculate_real_price,
    clean_data_pipeline
)
from .temporal_features import (
    convert_date_features,
    create_property_age_features,
    create_cyclic_temporal_features,
    add_crisis_period
)
from .derived_features import (
    create_price_derived_features,
    create_size_derived_features,
    add_region_flag,
    calculate_price_index,
    flag_low_coverage
)
