import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title('Анализ на координати')
st.subheader('1. Качване на файл с координати')

# Зареждане на файл
uploaded_file = st.file_uploader("Качете CSV/TXT файл", type=['csv','txt'])
if not uploaded_file:
    st.stop()

# Прочитане на данните
df = pd.read_csv(uploaded_file, header=None, names=['ID','X','Y','Z'])
st.success(f"Заредени са {len(df)} точки")

# Визуализация на всички точки
st.subheader('2. Визуализация на траекторията')
fig = go.Figure()
fig.add_trace(go.Scatter3d(
    x=df['X'], y=df['Y'], z=df['Z'],
    mode='lines+markers',
    marker=dict(size=4, color='blue'),
    line=dict(color='red', width=2),
    name='Траектория'
))
st.plotly_chart(fig, use_container_width=True)

# Търсене на кръгли коти
st.subheader('3. Търсене на кръгли коти')
step = st.number_input("Стъпка за Z-кота (параметър)", 
                     min_value=0.01, max_value=10.0, value=0.1, step=0.01)

if st.button("Намери кръгли коти"):
    # Намиране на всички Z стойности, кратни на step
    df['Z_rounded'] = (df['Z'] / step).round() * step
    rounded_points = df.groupby('Z_rounded').first().reset_index()
    
    st.write(f"Намерени {len(rounded_points)} кръгли коти със стъпка {step}:")
    st.dataframe(rounded_points[['ID','X','Y','Z']])
    
    # Визуализация на кръглите коти
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter3d(
        x=df['X'], y=df['Y'], z=df['Z'],
        mode='lines',
        line=dict(color='gray', width=1),
        name='Пълна траектория'
    ))
    fig2.add_trace(go.Scatter3d(
        x=rounded_points['X'],
        y=rounded_points['Y'],
        z=rounded_points['Z'],
        mode='markers',
        marker=dict(size=8, color='green'),
        name=f'Кръгли коти (стъпка {step})'
    ))
    st.plotly_chart(fig2, use_container_width=True)
    
    # Опция за експорт
    csv = rounded_points[['ID','X','Y','Z']].to_csv(index=False).encode()
    st.download_button(
        "Свали кръглите коти като CSV",
        csv,
        "rounded_z_coordinates.csv",
        "text/csv"
    )
