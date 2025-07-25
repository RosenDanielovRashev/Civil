import streamlit as st
import pandas as pd
import numpy as np

st.title("🎯 Филтриране на точки по коти")

# 1. Зареждане на файл с персонализирани настройки
uploaded_file = st.file_uploader("Качи файл с координати (CSV/TXT)", type=["csv", "txt"])
if uploaded_file:
    try:
        # Четене на файла без заглавен ред и задаване на имена на колони
        df = pd.read_csv(uploaded_file, header=None, names=["Point", "North", "East", "Elevation"])
        
        st.success(f"Заредени {len(df)} точки")
        st.dataframe(df.head())  # Показване на първите редове за проверка
        
        # 2. Въвеждане на параметри
        st.subheader("Параметри за филтриране")
        step = st.number_input("Кратност на котите (напр. 0.1)", min_value=0.01, value=0.1)
        tolerance = st.number_input("Диапазон (±)", min_value=0.01, value=0.05)
        
        # 3. Филтриране
        if st.button("Филтрирай"):
            # Конвертиране на Elevation в числов формат (ако има текстови стойности)
            df["Elevation"] = pd.to_numeric(df["Elevation"], errors='coerce')
            df = df.dropna(subset=["Elevation"])
            
            min_elev = df["Elevation"].min()
            max_elev = df["Elevation"].max()
            
            target_elevs = [round(x, 2) for x in np.arange(min_elev, max_elev + step, step)]
            
            filtered_points = []
            for target in target_elevs:
                mask = (df["Elevation"] >= target - tolerance) & (df["Elevation"] <= target + tolerance)
                filtered_df = df[mask].copy()
                filtered_df["Target_Elevation"] = target
                filtered_points.append(filtered_df)
            
            result_df = pd.concat(filtered_points)
            
            # 4. Експорт
            st.download_button(
                label="Свали резултатите (CSV)",
                data=result_df.to_csv(index=False, float_format="%.6f").encode(),
                file_name="filtered_elevations.csv"
            )
    
    except Exception as e:
        st.error(f"Грешка при обработка на файла: {str(e)}")
