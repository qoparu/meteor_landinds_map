import pandas as pd
import folium
from folium.features import MacroElement
from jinja2 import Template
from folium.plugins import MarkerCluster, HeatMapWithTime, Fullscreen, MiniMap
import numpy as np

blinking_dot_css = """
<style>
    .blinking-dot {
        width: 12px;
        height: 12px;
        background-color: #ff6b81;
        border-radius: 50%;
        border: 2px solid #ff4757;
        box-shadow: 0 0 10px #ff6b81, 0 0 15px #ff6b81;
        animation: blink 1.5s infinite ease-in-out;
    }
    @keyframes blink {
        0%, 100% {
            transform: scale(0.6);
            opacity: 0.7;
        }
        50% {
            transform: scale(1.0);
            opacity: 1;
        }
    }
    
    .small-meteorite { width: 8px; height: 8px; }
    .medium-meteorite { width: 12px; height: 12px; }
    .large-meteorite { width: 16px; height: 16px; }
    .huge-meteorite { width: 20px; height: 20px; background-color: #ff4757 !important; }
</style>
"""

nickname_html_css = """
{% macro html(this, kwargs) %}
<style>
    .nickname {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 20px;
        font-size: 24px;
        font-weight: bold;
        color: #fff;
        z-index: 1000;
        background: linear-gradient(90deg, #ff7e5f, #feb47b, #86a8e7, #7f7fd5, #91eae4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-animation 8s ease infinite;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .nickname:hover {
        transform: scale(1.1);
    }
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
<div class="nickname" title="Создатель карты">@qoparu</div>
{% endmacro %}
"""

hint_html_css = """
{% macro html(this, kwargs) %}
<style>
    .hint {
        position: fixed;
        top: 10px;
        right: 50px;
        padding: 8px 12px;
        background-color: rgba(0, 0, 0, 0.8);
        color: #fff;
        font-family: Arial, sans-serif;
        font-size: 13px;
        border-radius: 5px;
        border: 1px solid #91eae4;
        z-index: 1000;
        animation: fade-in 1s ease, pulse 3s infinite;
        max-width: 300px;
        line-height: 1.4;
    }
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { border-color: #91eae4; }
        50% { border-color: #ff6b81; }
    }
</style>
{% endmacro %}
"""

def load_and_optimize_data():
    try:
        print("Загружаем данные...")
        
        required_cols = ['name', 'reclat', 'reclong', 'year', 'mass', 'fall']
        df = pd.read_csv('meteorite-landings.csv', usecols=required_cols, low_memory=False)
        
        print(f"Загружено {len(df)} записей")
        
        mask = (
            pd.notna(df['reclat']) & 
            pd.notna(df['reclong']) & 
            pd.notna(df['year']) &
            ((df['reclat'] != 0) | (df['reclong'] != 0)) &
            (df['reclat'].between(-90, 90)) &
            (df['reclong'].between(-180, 180))
        )
        
        df_clean = df[mask].copy()
        
        # Обработка числовых данных
        df_clean['year'] = pd.to_numeric(df_clean['year'], errors='coerce')
        df_clean['mass'] = pd.to_numeric(df_clean['mass'], errors='coerce')
        
        # Убираем записи без года и массы
        df_clean.dropna(subset=['year', 'mass'], inplace=True)
        df_clean['year'] = df_clean['year'].astype(int)
        
        # ВАЖНО: масса уже в граммах, не делим на 1000 дважды!
        df_clean['mass_kg'] = (df_clean['mass'] / 1000).round(2)
        
        # Определяем категории размеров для разных иконок
        df_clean['size_category'] = pd.cut(
            df_clean['mass_kg'], 
            bins=[0, 1, 10, 100, float('inf')],
            labels=['small', 'medium', 'large', 'huge']
        )
        
        print(f"Подготовлено {len(df_clean)} валидных записей")
        return df_clean
        
    except FileNotFoundError:
        print("Ошибка: файл 'meteorite-landings.csv' не найден.")
        exit()
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
        exit()

def create_enhanced_stats_panel(df_clean):
    # Расчеты
    total_count = len(df_clean)
    total_mass_kg = df_clean['mass_kg'].sum()
    largest_meteorite = df_clean.loc[df_clean['mass_kg'].idxmax()]
    oldest_meteorite = df_clean.loc[df_clean['year'].idxmin()]
    newest_meteorite = df_clean.loc[df_clean['year'].idxmax()]
    
    # Подсчет по типам
    fall_count = df_clean[df_clean['fall'] == 'Fell'].shape[0] if 'fall' in df_clean.columns else 0
    found_count = df_clean[df_clean['fall'] == 'Found'].shape[0] if 'fall' in df_clean.columns else 0
    
    # Статистика по размерам
    size_stats = df_clean['size_category'].value_counts()
    
    # Среднее значение
    avg_mass = df_clean['mass_kg'].mean()
    
    return f"""
    <style>
        .stats-panel {{
            position: fixed;
            top: 10px;
            left: 10px;
            width: 320px;
            padding: 15px;
            background: linear-gradient(145deg, rgba(20, 20, 40, 0.95), rgba(40, 40, 80, 0.95));
            border: 2px solid #7f7fd5;
            border-radius: 15px;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 13px;
            z-index: 1000;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
        }}
        .stats-panel h3 {{
            margin: 0 0 15px 0;
            font-size: 18px;
            color: #91eae4;
            text-align: center;
            border-bottom: 2px solid #7f7fd5;
            padding-bottom: 8px;
            text-shadow: 0 0 10px rgba(145, 234, 228, 0.5);
        }}
        .stats-row {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 4px 0;
        }}
        .stats-label {{
            color: #feb47b;
            font-weight: bold;
        }}
        .stats-value {{
            color: #ffffff;
            text-align: right;
        }}
        .size-distribution {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #7f7fd5;
        }}
        .size-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .size-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #ff6b81;
            margin-right: 8px;
        }}
    </style>
    <div class="stats-panel">
        <h3>📊 Статистика Метеоритов</h3>
        
        <div class="stats-row">
            <span class="stats-label">Всего записей:</span>
            <span class="stats-value">{total_count:,}</span>
        </div>
        
        <div class="stats-row">
            <span class="stats-label">Общая масса:</span>
            <span class="stats-value">{total_mass_kg:,.0f} кг</span>
        </div>
        
        <div class="stats-row">
            <span class="stats-label">Средняя масса:</span>
            <span class="stats-value">{avg_mass:.1f} кг</span>
        </div>
        
        <div class="stats-row">
            <span class="stats-label">Самый крупный:</span>
            <span class="stats-value">{largest_meteorite['name'][:15]}...</span>
        </div>
        
        <div class="stats-row">
            <span class="stats-label">Масса крупнейшего:</span>
            <span class="stats-value">{largest_meteorite['mass_kg']:,.0f} кг</span>
        </div>
        
        <div class="stats-row">
            <span class="stats-label">Период данных:</span>
            <span class="stats-value">{oldest_meteorite['year']}-{newest_meteorite['year']}</span>
        </div>
        
        {f'''<div class="stats-row">
            <span class="stats-label">Падения (Fell):</span>
            <span class="stats-value">{fall_count:,}</span>
        </div>
        <div class="stats-row">
            <span class="stats-label">Находки (Found):</span>
            <span class="stats-value">{found_count:,}</span>
        </div>''' if fall_count > 0 or found_count > 0 else ''}
        
        <div class="size-distribution">
            <div style="color: #91eae4; font-weight: bold; margin-bottom: 8px;">Распределение по размерам:</div>
            {chr(10).join([f'<div class="size-item"><div class="size-dot"></div><span style="font-size: 11px;">{"< 1 кг" if cat == "small" else "1-10 кг" if cat == "medium" else "10-100 кг" if cat == "large" else "> 100 кг"}: {count:,}</span></div>' for cat, count in size_stats.items()])}
        </div>
    </div>
    """

def create_size_legend():
    return """
    <style>
        .size-legend {
            position: fixed;
            bottom: 80px;
            left: 10px;
            width: 200px;
            padding: 12px;
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #91eae4;
            border-radius: 10px;
            color: white;
            font-family: Arial;
            font-size: 12px;
            z-index: 1000;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 6px 0;
        }
        .legend-dot {
            border-radius: 50%;
            background: #ff6b81;
            margin-right: 10px;
            border: 1px solid #ff4757;
        }
    </style>
    <div class="size-legend">
        <h4 style="margin: 0 0 10px 0; color: #91eae4;">🌠 Размеры метеоритов</h4>
        <div class="legend-item">
            <div class="legend-dot" style="width: 8px; height: 8px;"></div>
            <span>< 1 кг</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="width: 12px; height: 12px;"></div>
            <span>1 - 10 кг</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="width: 16px; height: 16px;"></div>
            <span>10 - 100 кг</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="width: 20px; height: 20px; background: #ff4757;"></div>
            <span>> 100 кг</span>
        </div>
    </div>
    """

df_clean = load_and_optimize_data()

m = folium.Map(
    location=[40, 40], 
    zoom_start=3, 
    tiles='CartoDB dark_matter',
    prefer_canvas=True  # Лучше для производительности
)

m.get_root().html.add_child(folium.Element(blinking_dot_css))
m.get_root().html.add_child(folium.Element(create_enhanced_stats_panel(df_clean)))
m.get_root().html.add_child(folium.Element(create_size_legend()))

# Макроэлементы
macro_nickname = MacroElement()
macro_nickname._template = Template(nickname_html_css)
m.add_child(macro_nickname)

macro_hint = MacroElement()
macro_hint._template = Template(hint_html_css)
m.add_child(macro_hint)

# --- ОПТИМИЗИРОВАННЫЙ СЛОЙ КЛАСТЕРОВ ---
print("Создаем оптимизированный слой кластеров...")
marker_cluster_layer = folium.FeatureGroup(name="🌍 Все метеориты (кластеры)", show=True)

# Ограничиваем количество маркеров для производительности
max_markers = 15000
if len(df_clean) > max_markers:
    print(f"Ограничиваем до {max_markers} маркеров для лучшей производительности")
    # Берем самые крупные метеориты + случайную выборку
    large_meteorites = df_clean[df_clean['mass_kg'] > 10].copy()
    remaining_slots = max_markers - len(large_meteorites)
    if remaining_slots > 0:
        small_sample = df_clean[df_clean['mass_kg'] <= 10].sample(
            n=min(remaining_slots, len(df_clean[df_clean['mass_kg'] <= 10])),
            random_state=42
        )
        df_to_plot = pd.concat([large_meteorites, small_sample])
    else:
        df_to_plot = large_meteorites.head(max_markers)
else:
    df_to_plot = df_clean

cluster = MarkerCluster(
    options={
        'spiderfyOnMaxZoom': True,
        'showCoverageOnHover': False,
        'zoomToBoundsOnClick': True
    }
).add_to(marker_cluster_layer)

# Оптимизированное добавление маркеров
print(f"Добавляем {len(df_to_plot)} маркеров...")

for index, row in df_to_plot.iterrows():
    # Создаем popup с улучшенной информацией
    popup_text = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin-top: 0; color: #2c3e50;">{row['name']}</h4>
            <p><b>🌠 Масса:</b> {row['mass_kg']:,.1f} кг</p>
            <p><b>📅 Год:</b> {int(row['year'])}</p>
            <p><b>📍 Координаты:</b> {row['reclat']:.2f}, {row['reclong']:.2f}</p>
            {f"<p><b>🔍 Тип:</b> {row['fall']}</p>" if 'fall' in row and pd.notna(row['fall']) else ''}
        </div>
    """
    
    # Выбираем класс иконки в зависимости от размера
    size_class = f"{row['size_category']}-meteorite" if pd.notna(row['size_category']) else "small-meteorite"
    icon = folium.DivIcon(html=f'<div class="blinking-dot {size_class}"></div>')
    
    folium.Marker(
        location=[row['reclat'], row['reclong']],
        popup=folium.Popup(popup_text, max_width=300),
        icon=icon
    ).add_to(cluster)

m.add_child(marker_cluster_layer)

# --- УЛУЧШЕННАЯ ТЕПЛОВАЯ КАРТА ---
print("Создаем тепловую карту с анимацией...")

# Ограничиваем данные для анимации (для производительности)
heatmap_data_limit = 8000
if len(df_clean) > heatmap_data_limit:
    df_heatmap = df_clean.sample(n=heatmap_data_limit, random_state=42)
else:
    df_heatmap = df_clean

time_indexed_data = []
years = sorted(df_heatmap['year'].unique())
year_index = [str(year) for year in years]

for year in years:
    year_data = df_heatmap[df_heatmap['year'] == year]
    # Добавляем вес на основе массы
    points = []
    for _, row in year_data.iterrows():
        weight = min(np.log10(row['mass_kg'] + 1) / 3, 1.0)  # Нормализованный вес
        points.append([row['reclat'], row['reclong'], weight])
    time_indexed_data.append(points)

heatmap_layer = folium.FeatureGroup(name="🔥 Тепловая карта по годам", show=False)
HeatMapWithTime(
    data=time_indexed_data,
    index=year_index,
    radius=12,
    auto_play=False,
    max_opacity=0.8,
    gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
).add_to(heatmap_layer)
m.add_child(heatmap_layer)

# --- ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ ---
# Полноэкранный режим
Fullscreen(position='topright').add_to(m)

# Мини-карта для навигации
MiniMap(toggle_display=True, position='bottomright').add_to(m)

# Контроллер слоев
folium.LayerControl(collapsed=False, position='topright').add_to(m)

# --- СОХРАНЕНИЕ ---
output_file = 'meteorite_map_all_data.html'
m.save(output_file)

print(f"\n✅ Карта со ВСЕМИ данными создана: '{output_file}'")
print(f"📊 Общая статистика:")
print(f"   • Всего метеоритов на карте: {len(df_to_plot):,}")
print(f"   • Данных для тепловой карты: {len(df_heatmap):,}")
print(f"   • Временной период: {int(df_clean['year'].min())}-{int(df_clean['year'].max())}")
print(f"   • Общая масса: {df_clean['mass_kg'].sum():,.0f} кг")
print("\n⏱️  Время загрузки карты может составить 30-60 секунд в зависимости от размера данных")
