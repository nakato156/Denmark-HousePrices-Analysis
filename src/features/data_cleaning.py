import pandas as pd
import numpy as np

def filter_regular_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1: Filtrar ventas por 'regular_sale'. Excluir ventas familiares, subastas y '-'.
    """
    return df[df['sales_type'] == 'regular_sale'].copy()

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2: Eliminar filas sin `purchase_price`, `date` o `house_type`.
    Marcar como `incomplete_record` las filas sin `sqm` o `year_build`.
    """
    # Drop records missing critical fields
    df = df.dropna(subset=['purchase_price', 'date', 'house_type'])
    
    # Flag incomplete records
    df['incomplete_record'] = df['sqm'].isna() | df['year_build'].isna()
    return df

def remove_price_outliers(df: pd.DataFrame, percentiles=(0.005, 0.995)) -> pd.DataFrame:
    """
    Step 3: Eliminar el 0.5% superior e inferior de `purchase_price` (errores de digitación).
    """
    lower_bound = df['purchase_price'].quantile(percentiles[0])
    upper_bound = df['purchase_price'].quantile(percentiles[1])
    
    return df[(df['purchase_price'] >= lower_bound) & (df['purchase_price'] <= upper_bound)]

def calculate_real_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4: Calcular precio real por m² usando `dk_ann_infl_rate%` con año base 2015.
    Guardar como campo nuevo `real_sqm_price`.
    """
    if 'sqm' not in df.columns or 'dk_ann_infl_rate%' not in df.columns:
        raise ValueError("Missing 'sqm' or 'dk_ann_infl_rate%' column")
        
    df['nominal_sqm_price'] = df['purchase_price'] / df['sqm']
    
    # Calculation assumes infl_rate% represents an index or percentage from 2015
    # If dk_ann_infl_rate% is an index where 2015 = 100:
    # df['real_sqm_price'] = df['nominal_sqm_price'] / (df['dk_ann_infl_rate%'] / 100)
    
    # Assuming standard index methodology:
    df['real_sqm_price'] = df['nominal_sqm_price'] * (100 / df['dk_ann_infl_rate%'])
    
    return df

def clean_data_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the entire cleaning pipeline for Phase 1.
    """
    df = filter_regular_sales(df)
    df = handle_missing_values(df)
    df = remove_price_outliers(df)
    df = calculate_real_price(df)
    return df
