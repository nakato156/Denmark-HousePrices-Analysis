import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import os
import traceback
import pandas as pd
import numpy as np
from src.config import DATA_FILE, TABLES_DIR
from src.data_pipeline import run_phase_1_2_pipeline, execute_analytical_blocks

def main():
    print(f"Cargando dataset original: {DATA_FILE}")
    try:
        df = pd.read_parquet(DATA_FILE)
        print(f"Datos originales cargados. Total de filas: {len(df)}")
        
        # Ejecutar pipeline Fases 1 y 2
        df_clean = run_phase_1_2_pipeline(df)
        print("\\nPipeline Fase 1 y 2 ejecutado exitosamente. Columnas resultantes:")
        print(list(df_clean.columns))
        
        # Ejecutar bloques analíticos A, B, C y D
        res = execute_analytical_blocks(df_clean)
        print("\\nPipeline Bloques Analíticos ejecutados exitosamente!")
        
        # Guardar CSVs para Tableau
        os.makedirs(TABLES_DIR, exist_ok=True)
        
        # 1. Dataset limpio de transacciones
        df_clean.to_csv(TABLES_DIR / "dataset_limpio_transacciones.csv", index=False)
        print(f"Guardado: {TABLES_DIR / 'dataset_limpio_transacciones.csv'}")
        
        # 2. Índice trimestral de precios
        index_df = df_clean[['quarter_idx', 'region_type', 'house_type', 'price_index_1992']].drop_duplicates()
        index_df.to_csv(TABLES_DIR / "indice_trimestral_precios.csv", index=False)
        print(f"Guardado: {TABLES_DIR / 'indice_trimestral_precios.csv'}")
        
        # 3. Ratio de brecha Capital/Provincias
        ratio_df = res['block_b']['ratio_df']
        ratio_df.to_csv(TABLES_DIR / "ratio_brecha_regional.csv", index=False)
        print(f"Guardado: {TABLES_DIR / 'ratio_brecha_regional.csv'}")
        
        # 4. Tabla de drawdown por tipología
        drawdown_df = res['block_d']['drawdown_df']
        drawdown_df.to_csv(TABLES_DIR / "drawdown_por_tipologia.csv", index=False)
        print(f"Guardado: {TABLES_DIR / 'drawdown_por_tipologia.csv'}")
        
        print("\\n¡Todo el flujo fue completado y los exports de Tableau están listos en results/tablas/!")
        
    except Exception as e:
        print(f"Error corriendo pipeline: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
