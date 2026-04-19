import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def aggregate_for_causality(df: pd.DataFrame, region_col='region_type', date_col='date'):
    """
    Agrupa los datos por trimestre y región para el análisis de causalidad.
    """
    if 'quarter_idx' not in df.columns:
        df['quarter_idx'] = pd.to_datetime(df[date_col]).dt.to_period("Q")
        
    agg_funcs = {'real_sqm_price': 'median'}
    macro_vars = ['dk_ann_infl_rate%', 'bond_yield', 'nominal_rate']
    for v in macro_vars:
        if v in df.columns:
            agg_funcs[v] = 'mean'
            
    grouped = df.groupby(['quarter_idx', region_col]).agg(agg_funcs).reset_index()
    return grouped

def compare_regression_slopes(grouped_df: pd.DataFrame, macro_col='bond_yield', target_col='real_sqm_price'):
    """
    Compara la pendiente de regresión (vulnerabilidad/inelasticidad) entre Capital y Provincias.
    """
    results = []
    if macro_col not in grouped_df.columns:
        return pd.DataFrame()
        
    for region in grouped_df['region_type'].unique():
        region_data = grouped_df[grouped_df['region_type'] == region].dropna(subset=[macro_col, target_col])
        if len(region_data) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(region_data[macro_col], region_data[target_col])
            results.append({
                'region': region,
                'macro_variable': macro_col,
                'slope': slope,
                'r_value': r_value,
                'p_value': p_value
            })
    return pd.DataFrame(results)

def calculate_lagged_correlations_matrix(grouped_df: pd.DataFrame, target_col='real_sqm_price', max_lag=8):
    """
    Construye un heatmap de correlación con rezago (Variables macro vs Precio).
    Lags de 0 a 8 trimestres.
    """
    macro_vars = ['dk_ann_infl_rate%', 'bond_yield', 'nominal_rate']
    results = []
    
    # A nivel general (promediando regiones para evitar la mezcla de la brecha)
    general_df = grouped_df.groupby('quarter_idx').mean(numeric_only=True).reset_index()
    
    for var in macro_vars:
        if var not in general_df.columns:
            continue
        for lag in range(max_lag + 1):
            if lag == 0:
                corr = general_df[var].corr(general_df[target_col])
            else:
                # Shift del precio: Queremos ver si el yield de HOY afecta el precio del FUTURO (+lag)
                corr = general_df[var].corr(general_df[target_col].shift(-lag))
            results.append({
                'macro_variable': var,
                'lag': lag,
                'correlation': corr
            })
    
    if not results:
        return pd.DataFrame()
        
    res_df = pd.DataFrame(results)
    pivot_res = res_df.pivot(index='macro_variable', columns='lag', values='correlation')
    return pivot_res

def plot_causality_scatter(grouped_df: pd.DataFrame, macro_col='bond_yield', save_path=None):
    """
    Grafica el Yield vs Precio y su línea de regresión comparativa por Región.
    """
    if macro_col not in grouped_df.columns:
        return
        
    # Usando seaborn lmplot para conseguir los scatters + regresiones por hue
    g = sns.lmplot(data=grouped_df, x=macro_col, y='real_sqm_price', hue='region_type', 
                   height=6, aspect=1.3, scatter_kws={'alpha':0.5})
    g.fig.suptitle(f'Sensibilidad: {macro_col} vs Precio Real/m²', y=1.05)
    plt.grid(True, linestyle=':', alpha=0.6)
    
    if save_path:
        plt.savefig(save_path)

def run_causality_block_c(df: pd.DataFrame) -> dict:
    """
    Orquesta el Bloque C: Relación de causa entre métricas macro y precios.
    """
    print("--- Ejecutando Bloque C: Causalidad Macro -> Precios ---")
    grouped_df = aggregate_for_causality(df)
    slopes_df = compare_regression_slopes(grouped_df, macro_col='bond_yield')
    lag_matrix = calculate_lagged_correlations_matrix(grouped_df, max_lag=8)
    
    if not slopes_df.empty:
        print("\\n--- Pendientes de Regresión (Sensibilidad al Yield) ---")
        print(slopes_df[['region', 'slope', 'r_value', 'p_value']].to_string(index=False))
        
    return {
        'grouped_causality_data': grouped_df,
        'slopes': slopes_df,
        'lag_matrix': lag_matrix
    }
