import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

st.set_page_config(page_title="Филтриране и интерполация на точки", page_icon="📈")
st.title("📈 Филтриране и интерполация на точки по коти")

# 1. Зареждане на файл с персонализиран формат
uploaded_file = st.file_uploader("Качи файл с координати (CSV/TXT)", type=["csv", "txt"], 
                                help="Очакван формат: номер,North,East,Elevation разделени със запетаи")

if uploaded_file:
    try:
        # Четене на файла с персонализиран формат
        df = pd.read_csv(uploaded_file, header=None, names=["Point", "North", "East", "Elevation"])
        
        # Преобразуване на данните към числови типове
        df = df.apply(pd.to_numeric, errors='ignore')
        
        st.success(f"Успешно заредени {len(df)} точки")
        st.write("Преглед на данните:", df.head())
            
        # 2. Настройки за интерполация и филтриране
        st.subheader("Настройки за интерполация и филтриране")
        
        col1, col2 = st.columns(2)
        with col1:
            interpolation = st.checkbox("Интерполирай точки между съществуващите", value=True,
                                      help="Генерира допълнителни точки по правата между съществуващите точки")
        
        with col2:
            if interpolation:
                interp_step = st.number_input("Стъпка на интерполация (м)", min_value=0.1, value=5.0, step=0.1,
                                           help="Разстояние между интерполираните точки по правата")
        
        col3, col4 = st.columns(2)
        with col3:
            step = st.number_input("Кратност на котите", min_value=0.001, value=0.1, step=0.01)
        
        with col4:
            tolerance = st.number_input("Допуск (±)", min_value=0.001, value=0.05, step=0.01)
        
        # 3. Интерполация на точки (ако е избрана)
        if interpolation:
            st.subheader("Интерполация на точки")
            
            # Изчисляване на разстоянието между последователни точки
            df['Distance'] = np.sqrt(
                (df['North'].diff()**2 + 
                 df['East'].diff()**2 + 
                 df['Elevation'].diff()**2).cumsum().fillna(0)
            
            # Създаване на интерполационни функции
            f_north = interp1d(df['Distance'], df['North'], kind='linear')
            f_east = interp1d(df['Distance'], df['East'], kind='linear')
            f_elev = interp1d(df['Distance'], df['Elevation'], kind='linear')
            
            # Генериране на нови точки
            min_dist = df['Distance'].min()
            max_dist = df['Distance'].max()
            new_distances = np.arange(min_dist, max_dist, interp_step)
            
            new_points = pd.DataFrame({
                'Distance': new_distances,
                'North': f_north(new_distances),
                'East': f_east(new_distances),
                'Elevation': f_elev(new_distances),
                'Point': [f"INT_{i}" for i in range(len(new_distances))]
            })
            
            # Комбиниране на оригинални и интерполирани точки
            combined_df = pd.concat([df, new_points], ignore_index=True)
            combined_df = combined_df.sort_values('Distance')
            
            st.success(f"Генерирани {len(new_points)} интерполирани точки (общо {len(combined_df)} точки)")
            st.write("Преглед на интерполираните точки:", combined_df.tail())
            
            df_to_filter = combined_df
        else:
            df_to_filter = df
        
        # 4. Филтриране по коти
        if st.button("Филтрирай", type="primary"):
            with st.spinner("Филтриране на точки..."):
                min_elev = float(df_to_filter["Elevation"].min())
                max_elev = float(df_to_filter["Elevation"].max())
                
                target_elevs = [round(x, 3) for x in np.arange(min_elev, max_elev + step, step)]
                
                filtered_points = []
                for target in target_elevs:
                    mask = (df_to_filter["Elevation"] >= target - tolerance) & \
                           (df_to_filter["Elevation"] <= target + tolerance)
                    filtered_df = df_to_filter[mask].copy()
                    if not filtered_df.empty:
                        filtered_df["Target_Elevation"] = target
                        filtered_df["Elevation_Diff"] = filtered_df["Elevation"] - target
                        filtered_points.append(filtered_df)
                
                if filtered_points:
                    result_df = pd.concat(filtered_points)
                    result_df = result_df.sort_values(by=["Target_Elevation", "Elevation_Diff"])
                    
                    st.success(f"Намерени {len(result_df)} точки, отговарящи на критериите")
                    
                    # Визуализация на резултатите
                    st.subheader("Резултати")
                    st.dataframe(result_df.head(100))
                    
                    # Експорт
                    csv = result_df.to_csv(index=False, sep=',', float_format='%.4f').encode('utf-8')
                    st.download_button(
                        label="Свали CSV",
                        data=csv,
                        file_name="filtered_elevations.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("Не са намерени точки, отговарящи на критериите за филтриране")
    
    except Exception as e:
        st.error(f"Грешка при обработка на файла: {str(e)}")
        st.stop()
