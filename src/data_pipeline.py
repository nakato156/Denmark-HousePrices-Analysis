import pandas as pd
from .config import DATA_FILE

from .features.data_cleaning import clean_data_pipeline
from .features.temporal_features import add_crisis_period
from .features.derived_features import add_region_flag, calculate_price_index, flag_low_coverage

def run_phase_1_2_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta la Fase 1 (Limpieza y preparación) y la Fase 2 (Variables de contexto) 
    definidas en el plan de análisis.
    
    Devuelve el dataset enriquecido y listo para los Bloques A-D.
    """
    print("Iniciando Fase 1: Limpieza y preparación...")
    # Fase 1
    df = clean_data_pipeline(df)
    print(f"Fase 1 completada. Total registros limpios (regular_sale): {len(df)}")
    
    print("Iniciando Fase 2: Variables de contexto...")
    # Fase 2
    # 1. Período de crisis (5 épocas)
    df = add_crisis_period(df, date_col='date')
    
    # 2. Flag Capital vs Provincias
    df = add_region_flag(df, area_col='area')
    
    # 3. Índice de precio (base 1992Q1 = 100)
    df = calculate_price_index(df, date_col='date', type_col='house_type', region_col='region_type')
    
    # 4. Flaguear regiones/año con poca densidad (< 50 transacciones)
    df = flag_low_coverage(df, date_col='date', region_col='region_type')
    
    print("Fase 2 completada.")
    return df

def execute_analytical_blocks(df: pd.DataFrame):
    """
    Ejecuta analítica agregada para los Bloques A, B, C y D.
    Este paso espera que df sea la salida de `run_phase_1_2_pipeline(df)`.
    """
    from .analysis.macro_analysis import run_macro_analysis_block_a
    from .analysis.regional_analysis import run_regional_analysis_block_b
    from .analysis.causality_analysis import run_causality_block_c
    from .analysis.typology_analysis import run_typology_block_d
    
    block_a_res = run_macro_analysis_block_a(df)
    block_b_res = run_regional_analysis_block_b(df)
    block_c_res = run_causality_block_c(df)
    block_d_res = run_typology_block_d(df)
    
    return {
        'block_a': block_a_res,
        'block_b': block_b_res,
        'block_c': block_c_res,
        'block_d': block_d_res
    }

if __name__ == "__main__":
    # Test loading and executing pipeline
    print(f"Cargando {DATA_FILE}...")
    # Optional logic for when the script is tested directly.
    pass
