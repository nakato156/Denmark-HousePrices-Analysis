# Entregable 1: Perfilado y Limpieza de Datos

## 1. Perfilado de Datos (Dataset Profiling)
El dataset analizado corresponde a un histórico detallado de transacciones inmobiliarias en Dinamarca entre los años 1992 y 2024. Inicialmente, el conjunto de datos cuenta con aproximadamente 1.5 millones de registros en formato Parquet (`DKHousingPrices.parquet`). Contiene información crítica como precio de compra, fecha de transacción, tipo de propiedad, ubicación geográfica (municipio, región, código postal) y características físicas de las viviendas.

## 2. Unidad de Análisis
La unidad de análisis es la **transacción individual de compraventa de una propiedad**. Cada fila del dataset representa un evento único de cambio de titularidad de un inmueble en una fecha específica y por un precio determinado.

## 3. Granularidad
La granularidad de los datos es a nivel de **propiedad individual por transacción**. Temporalmente, se registra la fecha exacta de la venta. Espacialmente, se dispone de información hasta el nivel de código postal y municipio (Kommune).

## 4. Diccionario de Datos (Principales Variables)
*   **purchase_price:** Precio de venta del inmueble (DKK). (Numérica continua)
*   **date:** Fecha en que se realizó la transacción. (Fecha)
*   **house_type:** Tipo de propiedad (ej. Villa, Apartamento, Casa adosada). (Categórica)
*   **sales_type:** Tipo de venta (ej. Almindeligt frit salg - venta libre normal). (Categórica)
*   **area:** Área construida o habitable en metros cuadrados. (Numérica continua)
*   **zip_code / kommune / region:** Identificadores geográficos. (Categórica/Ordinal)
*   **build_year:** Año de construcción de la propiedad. (Numérica discreta)

*Nota: Durante el proceso se han derivado nuevas variables explicativas como `real_sqm_price`, `período_de_crisis`, e `índice_de_precio`.*

## 5. Problemas de Calidad Detectados
Durante la exploración inicial se identificaron las siguientes incidencias:
*   **Ventas No Representativas:** Presencia de ventas entre familiares, subastas forenses u otros tipos de traspaso (`sales_type` distinto a venta libre) que distorsionan el valor real de mercado.
*   **Datos Faltantes (Nulos):** Registros críticos carentes de precio de compra, fecha de venta o tipo de vivienda.
*   **Valores Atípicos (Outliers):** Precios por metro cuadrado extremadamente bajos o altos, presuntamente originados por errores de digitación o propiedades anómalas.
*   **Celdas con Baja Cobertura:** Algunos trimestres o regiones presentan volúmenes de transacciones muy bajos (n < 50), lo cual podría generar volatilidad estadística en los índices calculados.

## 6. Reglas de Limpieza Implementadas
Se diseñó un pipeline de limpieza automatizado (`src/features/data_cleaning.py`) que aplica las siguientes reglas de negocio:
1.  **Filtro Etapa 1 (Ventas Regulares):** Retención exclusiva de registros donde `sales_type == 'Almindeligt frit salg'` (Venta libre normal).
2.  **Filtro Etapa 2 (Integridad Básica):** Eliminación de filas que presentan valores nulos en columnas esenciales: `purchase_price`, `date`, y `house_type`.
3.  **Filtro Etapa 3 (Tratamiento de Outliers):** Exclusión de transacciones anómalas recortando el 0.5% superior e inferior (percentiles 0.005 y 0.995) de la distribución de precios.
4.  **Derivación Económica:** Cálculo del precio real por metro cuadrado (`real_sqm_price`), ajustado por inflación.

## 7. Bitácora Inicial
*   **Inicio:** El dataset crudo consta de ~1.5 millones de filas.
*   **Limpieza:** Tras aplicar reglas de exclusión de ventas no regulares, eliminación de nulos y recorte de outliers, el dataset de trabajo se redujo sustancialmente.
*   **Resultado Final:** El pipeline de procesamiento (`data_pipeline.py`) generó exitosamente ~1.3M - 1.4M de registros limpios.
*   **Exportación:** Se han generado 4 archivos CSV en el directorio `results/tablas/` listos para su ingesta y visualización en Tableau.
