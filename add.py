import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

# Настройки на страницата
st.set_page_config(layout="wide")
st.title("📌 Анализ на геодезически координати")
st.write("Заредете файл с координати (ID,X,Y,Z) за визуализация и експорт")

# 1. Зареждане на файл
uploaded_file = st.file_uploader("Качете CSV/TXT файл", type=['csv','txt'])
if not uploaded_file:
    st.stop()

# Прочитане на данните
try:
    df = pd.read_csv(uploaded_file, header=None, names=['ID','X','Y','Z'])
except Exception as e:
    st.error(f"Грешка при четене на файла: {e}")
    st.stop()

st.success(f"✅ Успешно заредени {len(df)} точки")

# 2. Визуализация
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("3D Визуализация")
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=df['X'], y=df['Y'], z=df['Z'],
        mode='lines+markers',
        line=dict(color='royalblue', width=2),
        marker=dict(size=4, color='red'),
        name='Траектория'
    ))
    st.plotly_chart(fig, use_container_width=True, height=600)

# 3. Търсене на кръгли коти
with col2:
    st.subheader("Филтриране")
    step = st.number_input("Стъпка за Z-кота", 
                         min_value=0.001, value=0.1, step=0.01,
                         help="Търси Z стойности кратни на това число")
    
    tolerance = st.number_input("Допустимо отклонение (±)", 
                              min_value=0.0, value=0.001, step=0.001,
                              help="Допускова грешка при търсене")

    if st.button("Приложи филтър"):
        df['Z_rounded'] = (df['Z'] / step).round() * step
        filtered = df[np.abs(df['Z'] - df['Z_rounded']) <= tolerance]
        st.session_state.filtered_df = filtered

# 4. Експорт на данни
st.subheader("📤 Експорт на данни")
export_type = st.radio("Какви данни да се експортират:",
                      ["Всички точки", "Филтрирани точки"])

if export_type == "Филтрирани точки" and 'filtered_df' not in st.session_state:
    st.warning("Първо приложете филтър!")
    st.stop()

export_df = st.session_state.filtered_df if export_type == "Филтрирани точки" else df

# Избор на колони
cols = st.multiselect("Изберете колони за експорт",
                     export_df.columns.tolist(),
                     default=['ID','X','Y','Z'])

if cols:
    csv_data = export_df[cols].to_csv(index=False)
    st.download_button(
        label="⬇️ Свали CSV",
        data=csv_data,
        file_name=f"coordinates_{export_type.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        help="Експорт на избраните данни във формат CSV"
    )
else:
    st.warning("Изберете поне една колона за експорт")

# Показване на данните
st.subheader("🗃️ Преглед на данните")
st.dataframe(export_df[cols] if cols else export_df, height=300)
