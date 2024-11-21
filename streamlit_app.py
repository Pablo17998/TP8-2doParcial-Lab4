import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def mostrar_informacion_alumno():
    with st.container(border=True):
        st.markdown('**Legajo:** 55547')
        st.markdown('**Nombre:** Cabrera Pablo Daniel')
        st.markdown('**Comisión:** C7')

def load_data():
    try:
        st.write("Subir archivo CSV")
        archivo_subido = st.file_uploader("Drag and drop file here", type=['csv'])
        if archivo_subido is not None:
            df = pd.read_csv(archivo_subido)
            columnas_requeridas = ['Año', 'Mes', 'Producto', 'Unidades_vendidas', 'Ingreso_total', 'Costo_total']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            if columnas_faltantes:
                st.error(f"Faltan las siguientes columnas: {columnas_faltantes}")
                return None
            
            df['Fecha'] = pd.to_datetime(df['Año'].astype(str) + '-' + df['Mes'].astype(str).str.zfill(2) + '-01')
            return df
        return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.exception(e)
        return None

def plot_sales_trend(df, producto):
    try:
        df_producto = df[df['Producto'] == producto]
        st.write(f"Registros encontrados para {producto}: {len(df_producto)}")
        
        if len(df_producto) == 0:
            fig, ax = plt.subplots(figsize=(12, 6))  
            ax.text(0.5, 0.5, f'No hay datos disponibles para {producto}', 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_axis_off()
            return fig
        
        ventas_mensuales = df_producto.groupby('Fecha')['Unidades_vendidas'].sum().reset_index()
        
        if len(ventas_mensuales) < 2:
            fig, ax = plt.subplots(figsize=(12, 6)) 
            ax.text(0.5, 0.5, f'Datos insuficientes para graficar tendencia de {producto}', 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_axis_off()
            return fig
        
        fig, ax = plt.subplots(figsize=(12, 5)) 
        ax.grid(True, linestyle='-', alpha=0.3)
        
        x_numeric = np.arange(len(ventas_mensuales))
        
        ax.plot(ventas_mensuales['Fecha'], ventas_mensuales['Unidades_vendidas'], 
                marker='o', label=producto, color='blue', linewidth=1.5)
        
        z = np.polyfit(x_numeric, ventas_mensuales['Unidades_vendidas'], 1)
        p = np.poly1d(z)
        ax.plot(ventas_mensuales['Fecha'], p(x_numeric), 'r--', label='Tendencia', linewidth=1.5)
        
        ax.set_title('Evolución de Ventas Mensual', pad=20)
        ax.set_xlabel('Año-Mes')
        ax.set_ylabel('Unidades Vendidas')
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        st.error(f"Error en plot_sales_trend: {str(e)}")
        st.exception(e)
        fig, ax = plt.subplots(figsize=(20, 15))
        ax.text(0.5, 0.5, f'Error al generar el gráfico: {str(e)}', 
                horizontalalignment='center', verticalalignment='center')
        ax.set_axis_off()
        return fig

def main():
    st.set_page_config(layout="wide")
    
    st.header("Información del Alumno")
    mostrar_informacion_alumno()

    with st.sidebar:
        st.header("Cargar archivo de datos")
        df = load_data()
        
        if df is not None:
            st.write("Seleccionar Sucursal")
            branches = ['Todas'] + df['Sucursal'].unique().tolist()
            selected_branch = st.selectbox(label='Seleccionar Sucursal', 
                                           options=branches, 
                                           label_visibility='collapsed')
    
    if df is not None:
        st.header(f"Datos de {'Todas las Sucursales' if selected_branch == 'Todas' else selected_branch}")
        
        df_filtered = df if selected_branch == 'Todas' else df[df['Sucursal'] == selected_branch]
        
        productos = df_filtered['Producto'].unique()
        
        for producto in productos:
            with st.container(border=True):
                st.subheader(f"{producto}")
                datos_producto = df_filtered[df_filtered['Producto'] == producto]

                datos_producto['Precio_promedio'] = datos_producto['Ingreso_total'] / datos_producto['Unidades_vendidas']
                precio_promedio = datos_producto['Precio_promedio'].mean()
                
                precio_promedio_anual = datos_producto.groupby('Año')['Precio_promedio'].mean()
                variacion_precio_promedio_anual = precio_promedio_anual.pct_change().mean() * 100
                
                datos_producto['Ganancia'] = datos_producto['Ingreso_total'] - datos_producto['Costo_total']
                datos_producto['Margen'] = (datos_producto['Ganancia'] / datos_producto['Ingreso_total']) * 100
                margen_promedio = datos_producto['Margen'].mean()
                
                margen_promedio_anual = datos_producto.groupby('Año')['Margen'].mean()
                variacion_margen_promedio_anual = margen_promedio_anual.pct_change().mean() * 100
                
                unidades_promedio = datos_producto['Unidades_vendidas'].mean()
                unidades_vendidas = datos_producto['Unidades_vendidas'].sum()
                
                unidades_por_año = datos_producto.groupby('Año')['Unidades_vendidas'].sum()
                variacion_anual_unidades = unidades_por_año.pct_change().mean() * 100
                
                col1, col2 = st.columns([0.25, 0.75])
                
                with col1:
                    st.metric(label="Precio Promedio", value=f"${precio_promedio:,.0f}".replace(",", "."), delta=f"{variacion_precio_promedio_anual:.2f}%")
                    st.metric(label="Margen Promedio", value=f"{margen_promedio:.0f}%".replace(",", "."), delta=f"{variacion_margen_promedio_anual:.2f}%")
                    st.metric(label="Unidades Vendidas", value=f"{unidades_vendidas:,.0f}".replace(",", "."), delta=f"{variacion_anual_unidades:.2f}%")
                
                with col2:
                    fig = plot_sales_trend(datos_producto, producto)
                    st.pyplot(fig)

if __name__ == "__main__":
    main()