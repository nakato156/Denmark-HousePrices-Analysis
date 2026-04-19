import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def group_regional_divergence(df: pd.DataFrame, region_col='region_type', date_col='date') -> pd.DataFrame:
    """
    Agrupa por trimestre y región para calcular precio mediano real/m².
    """
    if 'quarter_idx' not in df.columns:
        df['quarter_idx'] = pd.to_datetime(df[date_col]).dt.to_period("Q")

    regional_df = df.groupby(['quarter_idx', region_col]).agg(
        median_real_sqm=pd.NamedAgg(column='real_sqm_price', aggfunc='median')
    ).reset_index()
    
    return regional_df

def calculate_capital_ratio(regional_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula ratio Capital / Provincias por trimestre y encuentra el máximo histórico.
    """
    pivot_df = regional_df.pivot(index='quarter_idx', columns='region_type', values='median_real_sqm').reset_index()
    
    # Manejar caso si no existen ambas columnas
    if 'Capital' in pivot_df.columns and 'Provincias' in pivot_df.columns:
        pivot_df['ratio_capital_provincias'] = pivot_df['Capital'] / pivot_df['Provincias']
        
        # Encontrar máximo histórico
        max_idx = pivot_df['ratio_capital_provincias'].idxmax()
        max_row = pivot_df.loc[max_idx]
        
        print(f"--- Divergencia Regional Cúspide ---")
        print(f"Máximo Ratio Histórico Capital/Provincias: {max_row['ratio_capital_provincias']:.2f}")
        print(f"Ocurrió en: {max_row['quarter_idx']} (Año {max_row['quarter_idx'].year})")
        
        return pivot_df
    else:
        return pivot_df

def plot_regional_divergence(ratio_df: pd.DataFrame, save_path=None):
    """
    Grafica precio mediano real/m² Capital vs Provincias y el Ratio de divergenica.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # x axis timestamps
    x = ratio_df['quarter_idx'].dt.to_timestamp()
    
    # Plot 1: Absolute real median prices
    ax1.plot(x, ratio_df['Capital'], color='darkblue', linewidth=2, label='Capital')
    ax1.plot(x, ratio_df['Provincias'], color='darkorange', linewidth=2, label='Provincias')
    ax1.set_ylabel('Mediana Precio Real (kr/m²)', fontsize=12)
    ax1.set_title('Divergencia de Precios Absoluta (Capital vs Provincias)', fontsize=14)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend()
    
    # Plot 2: Ratio
    ax2.plot(x, ratio_df['ratio_capital_provincias'], color='purple', linewidth=2)
    # Shade crisis 2008-2012
    ax2.axvspan(pd.Timestamp('2008-01-01'), pd.Timestamp('2012-12-31'), color='red', alpha=0.1, label='Crisis Financiera')
    
    # Mark max point
    max_ratio = ratio_df['ratio_capital_provincias'].max()
    max_idx = ratio_df['ratio_capital_provincias'].idxmax()
    max_time = ratio_df.loc[max_idx, 'quarter_idx'].to_timestamp()
    ax2.scatter(max_time, max_ratio, color='red', s=50, zorder=5)
    ax2.annotate(f"{max_ratio:.2f}", (max_time, max_ratio), textcoords="offset points", xytext=(0,10), ha='center')
    
    ax2.set_ylabel('Ratio (Capital / Provincias)', fontsize=12)
    ax2.set_xlabel('Año', fontsize=12)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend()
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)

def calculate_recovery_speed(regional_df: pd.DataFrame) -> pd.DataFrame:
    """
    Mide velocidad de recuperación post-2008. ¿Cuántos trimestres tardó en recuperar el pico?
    Pico 2007: max price in 2007 or early 2008 before drop.
    """
    recovery_stats = []
    
    for region in regional_df['region_type'].unique():
        region_data = regional_df[regional_df['region_type'] == region].sort_values('quarter_idx')
        
        # Filtro hasta 2008 para encontrar el pico pre-crisis
        pre_crisis = region_data[region_data['quarter_idx'].dt.year <= 2008]
        if pre_crisis.empty:
            continue
            
        peak_idx = pre_crisis['median_real_sqm'].idxmax()
        peak_row = pre_crisis.loc[peak_idx]
        peak_price = peak_row['median_real_sqm']
        peak_q = peak_row['quarter_idx']
        
        # Buscar el primer trimestre post-pico donde el precio supere al pico
        post_crisis = region_data[region_data['quarter_idx'] > peak_q]
        recovery_row = post_crisis[post_crisis['median_real_sqm'] >= peak_price]
        
        if not recovery_row.empty:
            recovery_q = recovery_row.iloc[0]['quarter_idx']
            # Difference in quarters
            quarters_to_recover = (recovery_q.year - peak_q.year) * 4 + (recovery_q.quarter - peak_q.quarter)
            recovery_stats.append({'Region': region, 'Peak_Quarter': peak_q, 'Peak_Price': peak_price, 
                                   'Recovery_Quarter': recovery_q, 'Quarters_to_Recover': quarters_to_recover})
        else:
            recovery_stats.append({'Region': region, 'Peak_Quarter': peak_q, 'Peak_Price': peak_price, 
                                   'Recovery_Quarter': 'Not Recovered', 'Quarters_to_Recover': np.nan})
            
    return pd.DataFrame(recovery_stats)

def build_regional_heatmap(regional_df: pd.DataFrame, df_with_flag: pd.DataFrame):
    """
    Construir heatmap región × período con precio mediano real.
    (Evidencia visual de economía de dos velocidades).
    """
    if 'periodo_de_crisis' not in df_with_flag.columns:
        return
        
    # Order periods chronologically
    period_order = ['pre_liberalizacion', 'boom_hipotecario', 'crisis_financiera', 'recuperacion', 'post_covid']
    
    table = df_with_flag.pivot_table(index='region_type', columns='periodo_de_crisis', 
                                    values='real_sqm_price', aggfunc='median')
    
    # Reindex columns if they exist
    table = table.reindex(columns=[p for p in period_order if p in table.columns])
    
    # Plot heatmap
    plt.figure(figsize=(10, 4))
    sns.heatmap(table, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=.5)
    plt.title("Heatmap: Mediana de Precio Real (kr/m²) por Región y Periodo Histórico")
    plt.ylabel("Región")
    plt.xlabel("Periodo de Crisis")
    plt.tight_layout()
    # plt.show() # Para cuadernos

def run_regional_analysis_block_b(df: pd.DataFrame) -> dict:
    """
    Orquesta el Bloque B. Devuelve un diccionario con tablas.
    """
    print("--- Ejecutando Bloque B: Divergencia Regional ---")
    regional_df = group_regional_divergence(df)
    ratio_df = calculate_capital_ratio(regional_df)
    recovery_df = calculate_recovery_speed(regional_df)
    
    print("\n--- Velocidad de Recuperación (Post 2007) ---")
    print(recovery_df.to_string(index=False))
    
    # Return grouped tables for Tableau later
    return {
        'regional_df': regional_df,
        'ratio_df': ratio_df,
        'recovery_df': recovery_df
    }
