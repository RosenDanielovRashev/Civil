import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

st.set_page_config(page_title="Филтриране и интерполация на точки", page_icon="📈")
st.title("📈 Филтриране и интерполация на точки по коти")

# 1. Зареждане на файл с проверка на колоните
uploaded_file = st.file_uploader("Качи файл с координати (CSV/TXT)", type=["csv", "txt"], 
                                help="Файлът трябва да съдържа колони: Point, North, East, Elevation")

if uploaded_file:
    try:
        # Четене на файла
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:  # за txt файлове
            df = pd.read_csv(uploaded_file, delim_whitespace=True)
        
        # Проверка за задължителните колони
        required_columns = ["Point", "North", "East", "Elevation"]
        available_columns = [col.strip() for col in df.columns]
        
        # Проверка и стандартизиране на имената на колоните
        missing_columns = []
        for req_col in required_columns:
            if req_col not in available_columns and req_col.lower() not in [col.lower() for col in available_columns]:
                missing_columns.append(req_col)
        
        if missing_columns:
            st.error(f"Липсващи колони: {', '.join(missing_columns)}. Моля, проверете файла.")
            st.write("Налични колони:", df.columns.tolist())
        else:
            # Стандартизиране на имената на колоните
            df.columns = [col.strip() for col in df.columns]
            for req_col in required_columns:
                if req_col not in df.columns:
                    match = [col for col in df.columns if col.lower() == req_col.lower()]
                    if match:
                        df.rename(columns={match[0]: req_col}, inplace=True)
            
            st.success(f"Успешно заредени {len(df)} точки")
            
            # 2. Настройки за интерполация и филтриране
            st.subheader("Настройки за интерполация и филтриране")
            
            col1, col2 = st.columns(2)
            with col1:
                interpolation = st.checkbox("Интерполирай точки между съществуващите", value=True,
                                         help="Генерира допълнителни точки по правата между съществуващите точки")
            
            with col2:
                if interpolation:
                    interp_step = st.number_input("Стъпка на интерполация (м)", min_value=0.1, value=1.0, step=0.1,
                                                 help="Разстояние между интерполираните точки")
            
            col3, col4 = st.columns(2)
            with col3:
                step = st.number_input("Кратност на котите", min_value=0.001, value=0.1, step=0.01)
            
            with col4:
                tolerance = st.number_input("Допуск (±)", min_value=0.001, value=0.05, step=0.01)
            
            # 3. Интерполация на точки (ако е избрана)
            if interpolation:
                st.subheader("Интерполация на точки")
                
                # Сортираме точките по някакъв критерий (например по разстояние от началото)
                df['Distance'] = np.sqrt(df['North']**2 + df['East']**2)
                df = df.sort_values('Distance')
                
                # Създаваме интерполационни функции за всяка координата
                f_north = interp1d(df['Distance'], df['North'], kind='linear')
                f_east = interp1d(df['Distance'], df['East'], kind='linear')
                f_elev = interp1d(df['Distance'], df['Elevation'], kind='linear')
                
                # Генерираме нови точки с избраната стъпка
                min_dist = df['Distance'].min()
                max_dist = df['Distance'].max()
                new_distances = np.arange(min_dist, max_dist, interp_step)
                
                # Интерполираме новите точки
                new_points = pd.DataFrame({
                    'Distance': new_distances,
                    'North': f_north(new_distances),
                    'East': f_east(new_distances),
                    'Elevation': f_elev(new_distances),
                    'Point': [f"INT_{i}" for i in range(len(new_distances))]
                })
                
                # Комбинираме оригиналните и интерполираните точки
                combined_df = pd.concat([df, new_points], ignore_index=True)
                combined_df = combined_df.sort_values('Distance')
                
                st.success(f"Генерирани {len(new_points)} интерполирани точки (общо {len(combined_df)} точки)")
                st.write("Преглед на интерполираните точки:", combined_df.tail())
                
                # Използваме комбинирания DF за филтрирането
                df_to_filter = combined_df
            else:
                df_to_filter = df
            
            # 4. Филтриране по коти
            if st.button("Филтрирай", type="primary"):
                with st.spinner("Филтриране на точки..."):
                    min_elev = float(df_to_filter["Elevation"].min())
                    max_elev = float(df_to_filter["Elevation"].max())
                    
                    # Генериране на целеви коти
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
                        
                        # Статистика
                        st.write(f"**Общо целеви коти:** {len(target_elevs)}")
                        st.write(f"**Намерени точки:** {len(result_df)}")
                        st.write(f"**Интерполирани точки:** {len(new_points) if interpolation else 0}")
                        
                        # 5. Експорт
                        st.subheader("Експорт на резултатите")
                        
                        csv = result_df.to_csv(index=False, sep=',', encoding='utf-8').encode('utf-8')
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
