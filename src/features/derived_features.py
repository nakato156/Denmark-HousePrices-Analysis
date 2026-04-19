"""
Módulo para la creación de variables derivadas de precio y tamaño.
"""
import pandas as pd
import numpy as np

def create_price_derived_features(df: pd.DataFrame, price_col: str = 'purchase_price') -> pd.DataFrame:
    """
    Crea variables derivadas del precio.
    """
    df_result = df.copy()
    df_result['log_price'] = np.log1p(df_result[price_col])
    
    if 'region' in df_result.columns:
        regional_median = df_result.groupby('region')[price_col].transform('median')
        df_result['price_ratio_regional_median'] = df_result[price_col] / regional_median
    
    return df_result

def create_size_derived_features(df: pd.DataFrame, sqm_col: str = 'sqm', rooms_col: str = 'no_rooms') -> pd.DataFrame:
    """
    Crea variables derivadas del tamaño.
    """
    df_result = df.copy()
    df_result['sqm_per_room'] = df_result[sqm_col] / df_result[rooms_col].replace(0, 1) # Evitar división por cero
    return df_result

def add_region_flag(df: pd.DataFrame, area_col: str = 'area') -> pd.DataFrame:
    """
    Crea flag Capital vs Provincias.
    Copenhagen y área metropolitana = Capital.
    """
    df_result = df.copy()
    
    capital_areas = ['Copenhagen', 'København', 'Frederiksberg', 'Hovedstaden']
    
    # Check string contains any of capital areas 
    def is_capital(val):
        val_str = str(val).lower()
        for ca in capital_areas:
            if ca.lower() in val_str:
                return 'Capital'
        return 'Provincias'
        
    if area_col in df_result.columns:
        df_result['region_type'] = df_result[area_col].apply(is_capital)
    
    return df_result

def calculate_price_index(df: pd.DataFrame, date_col: str = 'date', type_col: str = 'house_type', region_col: str = 'region_type') -> pd.DataFrame:
    """
    Calcula un índice de precio trimestral por región y tipología donde Q1-1992 = 100.
    Permite comparar aceleración, no valor absoluto.
    """
    df_result = df.copy()
    
    # Ensure datetime to extract quarter
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])
        
    df_result['quarter_idx'] = df_result[date_col].dt.to_period("Q")
    
    # Group by quarter, region, and house type to find median
    grouped = df_result.groupby(['quarter_idx', region_col, type_col])['real_sqm_price'].median().reset_index()
    grouped.rename(columns={'real_sqm_price': 'median_real_sqm_price'}, inplace=True)
    
    # Extract base (1992 Q1)
    base_idx = grouped[grouped['quarter_idx'] == '1992Q1']
    base_idx = base_idx[[region_col, type_col, 'median_real_sqm_price']].rename(
        columns={'median_real_sqm_price': 'base_price_1992Q1'}
    )
    
    # Merge and calculate index
    grouped = pd.merge(grouped, base_idx, on=[region_col, type_col], how='left')
    grouped['price_index_1992'] = (grouped['median_real_sqm_price'] / grouped['base_price_1992Q1']) * 100
    
    # Drop existing price_index_1992 if any to avoid collision
    if 'price_index_1992' in df_result.columns:
        df_result.drop(columns=['price_index_1992'], inplace=True)
        
    # Join the index back to main df
    df_result = pd.merge(
        df_result, 
        grouped[['quarter_idx', region_col, type_col, 'price_index_1992']], 
        on=['quarter_idx', region_col, type_col], 
        how='left'
    )
    
    df_result.drop(columns=['quarter_idx'], inplace=True)
    
    return df_result

def flag_low_coverage(df: pd.DataFrame, date_col: str = 'date', region_col: str = 'region_type') -> pd.DataFrame:
    """
    Marca celdas con menos de 50 transacciones (región × año) como 'low_coverage'.
    """
    df_result = df.copy()
    
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])
    
    df_result['year_idx'] = df_result[date_col].dt.year
    
    # Count transactions per year and region
    counts = df_result.groupby(['year_idx', region_col]).size().reset_index(name='n_transactions')
    counts['low_coverage'] = counts['n_transactions'] < 50
    
    if 'low_coverage' in df_result.columns:
        df_result.drop(columns=['low_coverage'], inplace=True)
        
    df_result = pd.merge(
        df_result, 
        counts[['year_idx', region_col, 'low_coverage']], 
        on=['year_idx', region_col], 
        how='left'
    )
    
    df_result.drop(columns=['year_idx'], inplace=True)
    
    return df_result
