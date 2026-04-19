"""
Módulo para la creación de variables temporales.
"""
import pandas as pd
import numpy as np

def convert_date_features(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Convierte columna de fecha a datetime y extrae componentes temporales.
    """
    df_result = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])
    
    df_result['year_sale'] = df_result[date_col].dt.year
    df_result['month_sale'] = df_result[date_col].dt.month
    df_result['day_sale'] = df_result[date_col].dt.day
    df_result['dayofweek_sale'] = df_result[date_col].dt.dayofweek
    df_result['quarter_sale'] = df_result[date_col].dt.quarter
    
    season_map = {
        1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Autumn', 10: 'Autumn',
        11: 'Autumn', 12: 'Winter'
    }
    df_result['season_sale'] = df_result['month_sale'].map(season_map)
    return df_result

def create_property_age_features(df: pd.DataFrame, year_built_col: str = 'year_build', reference_year: int = 2024) -> pd.DataFrame:
    """
    Crea variables relacionadas con la edad de la propiedad.
    """
    df_result = df.copy()
    df_result['property_age'] = reference_year - df_result[year_built_col]
    df_result['decade_built'] = (df_result[year_built_col] // 10) * 10
    return df_result

def create_cyclic_temporal_features(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Crea variables temporales cíclicas (seno/coseno).
    """
    df_result = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])
        
    df_result['month_sin'] = np.sin(2 * np.pi * df_result[date_col].dt.month / 12)
    df_result['month_cos'] = np.cos(2 * np.pi * df_result[date_col].dt.month / 12)
    df_result['dayofweek_sin'] = np.sin(2 * np.pi * df_result[date_col].dt.dayofweek / 7)
    df_result['dayofweek_cos'] = np.cos(2 * np.pi * df_result[date_col].dt.dayofweek / 7)
    df_result['quarter_sin'] = np.sin(2 * np.pi * df_result[date_col].dt.quarter / 4)
    df_result['quarter_cos'] = np.cos(2 * np.pi * df_result[date_col].dt.quarter / 4)
    return df_result

def add_crisis_period(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Crear campo 'período de crisis' con 5 valores históricos.
    - pre_liberalizacion (<1995)
    - boom_hipotecario (1995–2007)
    - crisis_financiera (2008–2012)
    - recuperacion (2013–2019)
    - post_covid (2020+)
    """
    df_result = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])
        
    years = df_result[date_col].dt.year
    
    conditions = [
        years < 1995,
        (years >= 1995) & (years <= 2007),
        (years >= 2008) & (years <= 2012),
        (years >= 2013) & (years <= 2019),
        years >= 2020
    ]
    choices = ['pre_liberalizacion', 'boom_hipotecario', 'crisis_financiera', 'recuperacion', 'post_covid']
    df_result['periodo_de_crisis'] = np.select(conditions, choices, default='unknown')
    
    return df_result
