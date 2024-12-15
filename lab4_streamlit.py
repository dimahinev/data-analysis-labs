import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Функция для загрузки данных с кэшированием
@st.cache_data
def load_data():
    # Загрузка файла
    df = pd.read_excel("Wine Words.xlsx")
    
    # Очистка данных
    df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Преобразование price в число
    df['points'] = pd.to_numeric(df['points'], errors='coerce')  # Преобразование points в число
    
    # Заполнение пропусков медианой
    df['price'].fillna(df['price'].median(), inplace=True)
    df['points'].fillna(df['points'].median(), inplace=True)
    
    # Соотношение цена/качество
    df['price_quality_ratio'] = df['points'] / df['price'].replace(0, 1)
    
    # Очистка описания
    df['cleaned_description'] = df['description'].fillna("").str.lower()
    
    return df

# Загрузка данных
df = load_data()

# Заголовок приложения
st.title("📊 Приложение для анализа данных о винах")

# **Фильтры** на боковой панели
st.sidebar.header("🔍 Фильтры")
min_price, max_price = st.sidebar.slider("Диапазон цены (USD)", 0, int(df['price'].max()), (0, 100))
min_points, max_points = st.sidebar.slider("Диапазон баллов (Points)", 50, 100, (80, 95))
selected_category = st.sidebar.multiselect("Выберите категорию", df['category'].dropna().unique(), default=df['category'].dropna().unique())
min_quality = st.sidebar.slider("Минимальное соотношение цена/качество", 0.0, 10.0, 1.0)

# Применение фильтров
filtered_df = df[
    (df['price'] >= min_price) & 
    (df['price'] <= max_price) &
    (df['points'] >= min_points) & 
    (df['points'] <= max_points) &
    (df['category'].isin(selected_category)) &
    (df['price_quality_ratio'] >= min_quality)
]

# **Отображение данных**
st.subheader("📋 Отфильтрованные данные")
st.dataframe(filtered_df.head(1000))  # Показать первые 1000 строк

# **Визуализация 1: Гистограмма баллов**
st.subheader("1️⃣ Распределение баллов вин")
fig, ax = plt.subplots()
sns.histplot(filtered_df['points'], bins=20, kde=True, color='purple', ax=ax)
plt.xlabel("Points")
st.pyplot(fig)

# **Визуализация 2: Средние цены по странам**
st.subheader("2️⃣ Средние цены на вино по странам")
avg_price = filtered_df.groupby('country')['price'].mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots()
avg_price.plot(kind='bar', color='orange', ax=ax)
plt.title("Средние цены на вино по странам")
plt.ylabel("Средняя цена (USD)")
plt.xticks(rotation=45)
st.pyplot(fig)

# **Визуализация 3: Stacked Bar Chart (Категории и регионы)**
st.subheader("3️⃣ Распределение вин по категориям и регионам")
stacked_data = filtered_df.groupby(['province', 'category']).size().unstack(fill_value=0).head(10)
fig, ax = plt.subplots()
stacked_data.plot(kind='bar', stacked=True, colormap='viridis', ax=ax)
plt.title("Распределение вин по категориям и регионам")
plt.ylabel("Количество вин")
plt.xticks(rotation=45)
st.pyplot(fig)

# **Визуализация 4: Scatter Plot интерактивный**
st.subheader("4️⃣ Scatter Plot: Цена vs Баллы")
fig = px.scatter(
    filtered_df, x='price', y='points', color='category',
    title="Scatter Plot: Цена vs Баллы",
    hover_data=['country', 'variety', 'winery']
)
st.plotly_chart(fig)

# **Поиск по описанию вин**
st.subheader("🔎 Поиск вин по описанию")
search_term = st.text_input("Введите ключевое слово для поиска в описаниях:")
if search_term:
    search_results = df[df['cleaned_description'].str.contains(search_term.lower(), na=False)]
    st.write(f"Найдено {len(search_results)} вин с описанием, содержащим '{search_term}':")
    st.dataframe(search_results)
