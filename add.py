import streamlit as st
import pandas as pd

st.title("🎯 Филтриране на точки по коти")

# 1. Зареждане на файл
uploaded_file = st.file_uploader("Качи файл с координати (CSV/TXT)", type=["csv", "txt"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Заредени {len(df)} точки")
    
    # 2. Въвеждане на параметри
    st.subheader("Параметри за филтриране")
    step = st.number_input("Кратност на котите (напр. 0.1)", min_value=0.01, value=0.1)
    tolerance = st.number_input("Диапазон (±)", min_value=0.01, value=0.05)
    
    # 3. Филтриране
    if st.button("Филтрирай"):
        min_elev = df["Elevation"].min()
        max_elev = df["Elevation"].max()
        
        # Генериране на кратните коти
        target_elevs = [round(x, 2) for x in np.arange(min_elev, max_elev + step, step)]
        
        # Търсене на точки в диапазоните
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
            data=result_df.to_csv(index=False).encode(),
            file_name="filtered_elevations.csv"
        )
