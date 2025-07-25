import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title('Генериране на интерполирани точки')
st.header('1. Качване на файл с координати')

# Зареждане на файл
uploaded_file = st.file_uploader("Качете CSV/TXT файл (ID,X,Y,Z)", type=['csv','txt'])
if not uploaded_file:
    st.stop()

# Прочитане на данните
try:
    df = pd.read_csv(uploaded_file, header=None, names=['ID','X','Y','Z'])
except Exception as e:
    st.error(f"Грешка при четене на файла: {e}")
    st.stop()

st.success(f"✅ Успешно заредени {len(df)} точки")

# Параметри за търсене
st.header('2. Параметри за интерполация')
col1, col2 = st.columns(2)
with col1:
    step = st.number_input("Стъпка за Z-кота", 
                         min_value=0.001, value=1.0, step=0.1)
with col2:
    tolerance = st.number_input("Допустимо отклонение (±)", 
                              min_value=0.0, value=0.001, step=0.001)

# Функция за интерполация
def interpolate_points(df, step, tolerance):
    new_points = []
    for i in range(len(df)-1):
        p1, p2 = df.iloc[i], df.iloc[i+1]
        z_min, z_max = min(p1['Z'], p2['Z']), max(p1['Z'], p2['Z'])
        
        z_values = np.arange(
            np.ceil(z_min/step)*step,
            np.floor(z_max/step)*step + step/2,
            step
        )
        z_values = z_values[(z_values >= z_min - tolerance) & (z_values <= z_max + tolerance)]
        
        for z in z_values:
            ratio = (z - p1['Z']) / (p2['Z'] - p1['Z'])
            new_points.append([
                f"{p1['ID']}-{p2['ID']}",
                p1['X'] + ratio*(p2['X'] - p1['X']),
                p1['Y'] + ratio*(p2['Y'] - p1['Y']),
                z
            ])
    
    return pd.DataFrame(new_points, columns=['ID','X','Y','Z'])

if st.button("Генерирай точки"):
    interpolated_df = interpolate_points(df, step, tolerance)
    
    if not interpolated_df.empty:
        st.success(f"Намерени {len(interpolated_df)} интерполирани точки")
        
        # Визуализация
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=df['X'], y=df['Y'], z=df['Z'],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=4),
            name='Оригинални'
        ))
        fig.add_trace(go.Scatter3d(
            x=interpolated_df['X'],
            y=interpolated_df['Y'],
            z=interpolated_df['Z'],
            mode='markers',
            marker=dict(size=6, color='red'),
            name='Интерполирани'
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Експорт
        st.header("3. Експорт на резултати")
        export_format = st.radio("Формат:", ['CSV', 'TXT'])
        
        if export_format == 'CSV':
            data = interpolated_df.to_csv(index=False)
            file_ext = 'csv'
            mime_type = 'text/csv'
        else:
            data = interpolated_df.to_csv(index=False, sep=' ')  # TXT формат с интервали
            file_ext = 'txt'
            mime_type = 'text/plain'
        
        st.download_button(
            label=f"⬇️ Свали {export_format}",
            data=data,
            file_name=f"interpolated_points.{file_ext}",
            mime=mime_type
        )
        
        st.dataframe(interpolated_df)
    else:
        st.warning("Не са намерени точки за избраните параметри!")

st.header("Оригинални данни")
st.dataframe(df)
