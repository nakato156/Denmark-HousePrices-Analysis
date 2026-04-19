import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def group_transactions_by_quarter(df: pd.DataFrame, date_col='date') -> pd.DataFrame:
    """
    Agrupa transacciones por trimestre para calcular volumen y extraer series macro.
    Asume que las métricas macro ('dk_ann_infl_rate%', 'yield', 'nominal_rate') 
    son constantes por trimestre, por lo que usamos su media.
    """
    if 'quarter_idx' not in df.columns:
        df['quarter_idx'] = pd.to_datetime(df[date_col]).dt.to_period("Q")

    # Aggregations
    agg_funcs = {
        'purchase_price': 'count', # Volumen de transacciones
    }
    
    # Check what macro variables exist and add their mean
    macro_vars = ['dk_ann_infl_rate%', 'bond_yield', 'nominal_rate']
    for v in macro_vars:
        if v in df.columns:
            agg_funcs[v] = 'mean'
            
    quarterly_df = df.groupby('quarter_idx').agg(agg_funcs).reset_index()
    quarterly_df.rename(columns={'purchase_price': 'transaction_volume'}, inplace=True)
    
    # Sort chronologically
    return quarterly_df.sort_values('quarter_idx')

def plot_macro_series(quarterly_df: pd.DataFrame, save_path=None):
    """
    Grafica series macro (inflación, yield, nominal_rate) y volumen de transacciones 
    trimestral en el mismo eje temporal.
    """
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    x = quarterly_df['quarter_idx'].dt.to_timestamp()
    
    # Volume - bar plot on primary y-axis
    ax1.bar(x, quarterly_df['transaction_volume'], color='lightgray', alpha=0.6, width=60, label='Volumen de transacciones')
    ax1.set_ylabel('Transaction Volume', color='gray')
    ax1.tick_params(axis='y', labelcolor='gray')
    
    # Secondary y-axis for rates
    ax2 = ax1.twinx()
    colors = {'bond_yield': 'red', 'dk_ann_infl_rate%': 'blue', 'nominal_rate': 'green'}
    
    for col, color in colors.items():
        if col in quarterly_df.columns:
            ax2.plot(x, quarterly_df[col], color=color, linewidth=2, label=col)
            
    ax2.set_ylabel('Tasas (%)')
    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    
    # Add crisis shading (approximate dates based on Plan)
    # pre_liberalizacion (<1995), boom_hipotecario (1995–2007), crisis_financiera (2008–2012)
    # We will shade the 2008-2012 crisis as the main visual anchor
    ax2.axvspan(pd.Timestamp('2008-01-01'), pd.Timestamp('2012-12-31'), color='red', alpha=0.1, label='Crisis Financiera')
    
    fig.legend(loc='upper right', bbox_to_anchor=(0.90, 0.85))
    plt.title('Series Macro vs Volumen de Transacciones (1992 - 2024)', fontsize=16)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    # plt.show() # Disabled for headless, call in notebook if needed

def calculate_lagged_correlations(quarterly_df: pd.DataFrame, macro_col='bond_yield', target_col='transaction_volume', max_lag=4) -> pd.DataFrame:
    """
    Calcula la correlación con rezago entre una variable macro (ej. yield) y volumen.
    """
    results = []
    
    if macro_col not in quarterly_df.columns:
        return pd.DataFrame()
        
    for lag in range(1, max_lag + 1):
        # Shift volume to match current yield with future volume
        shifted_target = quarterly_df[target_col].shift(-lag)
        corr = quarterly_df[macro_col].corr(shifted_target)
        results.append({'macro_variable': macro_col, 'lag_quarters': lag, 'correlation': corr})
        
    res_df = pd.DataFrame(results)
    
    # Identify dominant lag (typically most negative for yield -> volume)
    if not res_df.empty:
        best_lag = res_df.loc[res_df['correlation'].idxmin()]
        print(f"Mejor rezago (correlación más negativa) {macro_col} -> {target_col}: ")
        print(f"Lag {best_lag['lag_quarters']} trimestres (r = {best_lag['correlation']:.2f})")
        
    return res_df

def run_macro_analysis_block_a(df: pd.DataFrame) -> dict:
    """
    Orquesta el Bloque A. Devuelve un diccionario con tablas y resultados.
    """
    print("--- Ejecutando Bloque A: Analisis Macro ---")
    quarterly_df = group_transactions_by_quarter(df)
    
    # Try with 'bond_yield', if it exists (or whatever the exact column name is)
    # For now, we return the function pointers so they can be run in the notebook 
    # when the actual column names are confirmed.
    
    # lag_corr_yield = calculate_lagged_correlations(quarterly_df, macro_col='bond_yield')
    
    return {
        'quarterly_grouped_data': quarterly_df
    }
