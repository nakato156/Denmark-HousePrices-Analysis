import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def group_by_typology(df: pd.DataFrame, date_col='date', type_col='house_type', region_col='region_type') -> pd.DataFrame:
    """
    Agrupa por trimestre, región y tipología
    """
    if 'quarter_idx' not in df.columns:
        df['quarter_idx'] = pd.to_datetime(df[date_col]).dt.to_period("Q")
        
    cols_to_agg = {'real_sqm_price': 'median'}
    if 'price_index_1992' in df.columns:
        cols_to_agg['price_index_1992'] = 'median'
        
    grouped = df.groupby(['quarter_idx', region_col, type_col]).agg(cols_to_agg).reset_index()
    return grouped

def calculate_drawdown(grouped_df: pd.DataFrame, type_col='house_type', region_col='region_type') -> pd.DataFrame:
    """
    Calcula el Drawdown: (mínimo 2008-2012 − pico 2007) / pico 2007 × 100
    """
    results = []
    
    for (region, htype), group in grouped_df.groupby([region_col, type_col]):
        group_df = group.sort_values('quarter_idx')
        
        # Pico < 2008 (o año 2007 particularmente)
        peak_2007_data = group_df[group_df['quarter_idx'].dt.year <= 2008]
        if peak_2007_data.empty:
            continue
        peak_2007 = peak_2007_data['real_sqm_price'].max()
        
        # Valle 2008-2012
        crisis_data = group_df[(group_df['quarter_idx'].dt.year >= 2008) & (group_df['quarter_idx'].dt.year <= 2012)]
        if crisis_data.empty:
            continue
        min_crisis = crisis_data['real_sqm_price'].min()
        
        # Drawdown en porcentaje
        drawdown = ((min_crisis - peak_2007) / peak_2007) * 100
        
        results.append({
            'region_type': region,
            'house_type': htype,
            'peak_2007_price': peak_2007,
            'min_2008_2012_price': min_crisis,
            'drawdown_pct': drawdown
        })
        
    return pd.DataFrame(results)

def calculate_typology_recovery(grouped_df: pd.DataFrame, type_col='house_type', region_col='region_type') -> pd.DataFrame:
    """
    Mide los trimestres hasta recuperar el precio pre-crisis por tipología × región.
    """
    results = []
    
    for (region, htype), group in grouped_df.groupby([region_col, type_col]):
        group = group.sort_values('quarter_idx')
        pre_crisis = group[group['quarter_idx'].dt.year <= 2008]
        if pre_crisis.empty:
            continue
            
        peak_idx = pre_crisis['real_sqm_price'].idxmax()
        peak_row = pre_crisis.loc[peak_idx]
        peak_price = peak_row['real_sqm_price']
        peak_q = peak_row['quarter_idx']
        
        post_crisis = group[group['quarter_idx'] > peak_q]
        recovery_row = post_crisis[post_crisis['real_sqm_price'] >= peak_price]
        
        if not recovery_row.empty:
            recovery_q = recovery_row.iloc[0]['quarter_idx']
            quarters = (recovery_q.year - peak_q.year) * 4 + (recovery_q.quarter - peak_q.quarter)
            rec_str = str(recovery_q)
        else:
            quarters = np.nan
            rec_str = 'Not Recovered'
            
        results.append({
            'region_type': region,
            'house_type': htype,
            'peak_quarter': peak_q,
            'recovery_quarter': rec_str,
            'quarters_to_recover': quarters
        })
        
    return pd.DataFrame(results)

def plot_drawdown_heatmap(drawdown_df: pd.DataFrame):
    """
    heatmap tipología × región visualizando el Drawdown
    """
    if drawdown_df.empty: return
    
    pivot_dd = drawdown_df.pivot(index='house_type', columns='region_type', values='drawdown_pct')
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_dd, annot=True, fmt=".1f", cmap="Reds_r", center=0, 
                cbar_kws={'label': 'Drawdown % (Mayor caída / Negative)'})
    plt.title("Max Drawdown (%) por Tipología y Región (Crisis 2008-2012)")
    plt.ylabel("Tipología")
    plt.xlabel("Región")
    plt.tight_layout()

def run_typology_block_d(df: pd.DataFrame) -> dict:
    """
    Orquesta el Bloque D: Resiliencia del activo inmobiliario por Tipología.
    """
    print("--- Ejecutando Bloque D: Resiliencia por Tipología ---")
    grouped_df = group_by_typology(df)
    drawdown_df = calculate_drawdown(grouped_df)
    recovery_df = calculate_typology_recovery(grouped_df)
    
    # Imprimiendo el resumen top caidas
    if not drawdown_df.empty:
        worst_drops = drawdown_df.sort_values('drawdown_pct').head(5)
        print("\\n--- Top 5 Peores Caídas de Precio (Drawdown) ---")
        print(worst_drops[['region_type', 'house_type', 'drawdown_pct']].to_string(index=False))
        
    return {
        'grouped_typology_data': grouped_df,
        'drawdown_df': drawdown_df,
        'recovery_df': recovery_df
    }
