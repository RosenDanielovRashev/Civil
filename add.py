import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title('Генериране на интерполирани точки')
st.header('1. Качване на файл с координати')

uploaded_file = st.file_uploader("Качете CSV/TXT файл с координати (ID,X,Y,Z)", type=['csv','txt'])
if not uploaded_file:
    st.stop()

# Прочитане на данните
df = pd.read_csv(uploaded_file, header=None, names=['ID','X','Y','Z'])
st.success(f"Заредени са {len(df)} точки")

# Параметри за търсене
st.header('2. Параметри за търсене')
step = st.number_input("Стъпка за Z-кота", min_value=0.001, value=1.0, step=0.1)
tolerance = st.number_input("Допустимо отклонение", min_value=0.0, value=0.001, step=0.001)

def find_interpolated_points(df, step, tolerance):
    new_points = []
    
    for i in range(len(df)-1):
        point1 = df.iloc[i]
        point2 = df.iloc[i+1]
        
        z_min = min(point1['Z'], point2['Z'])
        z_max = max(point1['Z'], point2['Z'])
        
        # Намираме всички кръгли стойности в този интервал
        first_z = np.ceil(z_min / step) * step
        last_z = np.floor(z_max / step) * step
        z_values = np.arange(first_z, last_z + step/2, step)
        
        # Филтрираме стойностите в допустимия диапазон
        z_values = z_values[(z_values >= z_min - tolerance) & (z_values <= z_max + tolerance)]
        
        # Интерполираме за всяка намерена Z стойност
        for z in z_values:
            ratio = (z - point1['Z']) / (point2['Z'] - point1['Z'])
            x = point1['X'] + ratio * (point2['X'] - point1['X'])
            y = point1['Y'] + ratio * (point2['Y'] - point1['Y'])
            
            new_points.append({
                'ID': f"{point1['ID']}-{point2['ID']}",
                'X': x,
                'Y': y,
                'Z': z,
                'Source': f"Интерполирана между {point1['ID']} и {point2['ID']}"
            })
    
    return pd.DataFrame(new_points)

if st.button("Намери интерполирани точки"):
    interpolated_df = find_interpolated_points(df, step, tolerance)
    
    if len(interpolated_df) > 0:
        st.success(f"Намерени са {len(interpolated_df)} нови точки!")
        
        # Визуализация
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=df['X'], y=df['Y'], z=df['Z'],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=4),
            name='Оригинални точки'
        ))
        fig.add_trace(go.Scatter3d(
            x=interpolated_df['X'],
            y=interpolated_df['Y'],
            z=interpolated_df['Z'],
            mode='markers',
            marker=dict(size=6, color='red'),
            name=f'Интерполирани точки (стъпка {step})'
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # Показване на таблица
        st.dataframe(interpolated_df)
        
        # Експорт
        csv = interpolated_df.to_csv(index=False).encode()
        st.download_button(
            "Свали интерполирани точки като CSV",
            csv,
            f"interpolated_points_step_{step}.csv",
            "text/csv"
        )
    else:
        st.warning("Не са намерени интерполирани точки за избраните параметри!")

st.header("Оригинални данни")
st.dataframe(df)
