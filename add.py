import streamlit as st
import pandas as pd
import numpy as np

st.title('Генериране на интерполирани точки')
st.header('1. Качване на файл с координати')

# Зареждане на файл (CSV или TXT)
uploaded_file = st.file_uploader("Качете CSV/TXT файл (ID,X,Y,Z)", type=['csv', 'txt'])
if not uploaded_file:
    st.stop()

# Прочитане на данните (работи с CSV и TXT)
try:
    df = pd.read_csv(uploaded_file, header=None, names=['ID', 'X', 'Y', 'Z'])
except Exception as e:
    st.error(f"Грешка при четене на файла: {e}")
    st.stop()

st.success(f"✅ Успешно заредени {len(df)} точки")

# Настройки за номериране
st.header('2. Настройки за номериране')
col1, col2 = st.columns(2)
with col1:
    step = st.number_input("Стъпка за Z-кота", min_value=0.001, value=1.0, step=0.1)
with col2:
    start_id = st.number_input("Начален номер на точките", min_value=0, value=5000, step=1)

# Функция за интерполация с променливи ID
def interpolate_points_with_ids(df, step, start_id=5000):
    new_points = []
    current_id = start_id
    
    for i in range(len(df)-1):
        p1, p2 = df.iloc[i], df.iloc[i+1]
        z_min, z_max = min(p1['Z'], p2['Z']), max(p1['Z'], p2['Z'])
        
        z_values = np.arange(
            np.ceil(z_min/step)*step,
            np.floor(z_max/step)*step + step/2,
            step
        )
        z_values = z_values[(z_values > z_min) & (z_values < z_max)]
        
        for z in z_values:
            ratio = (z - p1['Z']) / (p2['Z'] - p1['Z'])
            new_points.append([
                current_id,
                p1['X'] + ratio*(p2['X'] - p1['X']),
                p1['Y'] + ratio*(p2['Y'] - p1['Y']),
                round(z, 10)
            ])
            current_id += 1
    
    return pd.DataFrame(new_points, columns=['ID', 'X', 'Y', 'Z'])

if st.button("Генерирай точки"):
    interpolated_df = interpolate_points_with_ids(df, step, start_id)
    
    if not interpolated_df.empty:
        st.success(f"Намерени {len(interpolated_df)} интерполирани точки (ID от {start_id} до {start_id+len(interpolated_df)-1})")
        
        # Експорт в CSV и TXT
        st.header("3. Експорт на резултати")
        csv_data = interpolated_df.to_csv(index=False)
        txt_data = interpolated_df.to_csv(index=False, sep='\t')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Свали CSV",
                data=csv_data,
                file_name=f"interpolated_points_{start_id}_to_{start_id+len(interpolated_df)-1}.csv",
                mime='text/csv'
            )
        with col2:
            st.download_button(
                label="⬇️ Свали TXT",
                data=txt_data,
                file_name=f"interpolated_points_{start_id}_to_{start_id+len(interpolated_df)-1}.txt",
                mime='text/plain'
            )
        
        st.dataframe(interpolated_df)
    else:
        st.warning(f"Не са намерени точки със стъпка {step} в интервалите!")

st.header("Оригинални данни")
st.dataframe(df)
