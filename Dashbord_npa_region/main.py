import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

df = pd.read_excel('result.xlsx')
    # Функция для обновления графиков и индикаторов
def update_charts_and_indicators(selected_years):  
    start_year, end_year = selected_years
    filtered_df = df.query(f'Год >= {start_year} & Год <= {end_year}')
    
    total_acts_count = filtered_df[filtered_df['Категория'] == 'Вид документа']['Акт'].sum()
    active_acts_count = round(filtered_df[filtered_df['Значение'] == 'Действующий']['Акт'].sum() / total_acts_count * 100)
    inactive_acts_count = round(filtered_df[filtered_df['Значение'] == 'Недействующий']['Акт'].sum() / total_acts_count * 100)
    primary_acts_count = round(filtered_df[filtered_df['Значение'] == 'Основной']['Акт'].sum() / total_acts_count * 100)
    amending_acts_count = round(filtered_df[filtered_df['Значение'] == 'Изменяющий']['Акт'].sum() / total_acts_count * 100)
    
    yearly_data = filtered_df[filtered_df['Категория'] == 'Вид документа'].groupby('Год')['Акт'].sum().reset_index()
    index = pd.Index(range(start_year, end_year + 1), name='Год')
    yearly_data = yearly_data.set_index('Год').reindex(index, fill_value=0).reset_index()
    
    # Линейный график с улучшениями
    yearly_fig = px.line(yearly_data, x='Год', y='Акт', title='Общее количество НПА субъектов РФ по годам',
                          markers=True, line_shape='linear', 
                          template='plotly_white', color_discrete_sequence=['#1f77b4'])
    yearly_fig.update_layout(yaxis_title='Количество НПА субъектов РФ',yaxis_title_font=dict(size=14), xaxis_title_font=dict(size=14), xaxis_title='Год', height=662)
    
    # Гистограмма по федеральным округам с улучшениями
    subj_data = filtered_df[filtered_df['Категория'] == 'Субъект РФ'].groupby('Федеральный округ')[['Акт']].sum().reset_index().sort_values(by='Акт', ascending=True)
    subject_fig = go.Figure(data=[go.Bar(x=subj_data['Акт'], y=subj_data['Федеральный округ'], orientation='h',
                                          marker_color='#ff7f0e')])
    subject_fig.update_layout(title='Количество НПА субъектов РФ по федеральным округам',
                              yaxis_title='Федеральный округ', xaxis_title='Количество НПА субъектов РФ', yaxis_title_font=dict(size=14), xaxis_title_font=dict(size=14),
                              template='plotly_white', height=662)
    
    # Добавляем надписи со значениями для гистограммы по федеральным округам
    for i in range(len(subj_data)):
        subject_fig.add_annotation(x=subj_data['Акт'].iloc[i], 
                                   y=subj_data['Федеральный округ'].iloc[i], 
                                   text=str(subj_data['Акт'].iloc[i]), 
                                   showarrow=False, 
                                   xanchor='left', 
                                   font=dict(size=12))

    # Гистограмма по видам документа с улучшениями
    doc_data = filtered_df[filtered_df['Категория'] == 'Вид документа'].groupby(['Значение'])['Акт'].sum().reset_index().sort_values(by='Акт', ascending=False).head(6)    
    document_fig = go.Figure(data=[go.Bar(x=doc_data['Значение'], y=doc_data['Акт'], orientation='v',
                                           marker_color='#2ca02c')])
    document_fig.update_layout(title='Количество НПА субъектов РФ по видам документа',
                               yaxis_title='Количество НПА субъектов РФ', xaxis_title='Вид НПА субъекта РФ', yaxis_title_font=dict(size=14), xaxis_title_font=dict(size=14),
                               template='plotly_white', height=662)
    
    # Добавляем надписи со значениями для гистограммы по видам документа
    for i in range(len(doc_data)):
        document_fig.add_annotation(x=doc_data['Значение'].iloc[i], 
                                    y=doc_data['Акт'].iloc[i], 
                                    text=str(doc_data['Акт'].iloc[i]), 
                                    showarrow=False, 
                                    yanchor='bottom',
    font=dict(size=12))

    # Круговая диаграмма с улучшениями
    status_data = filtered_df[filtered_df['Категория'] == 'Статус действия документа'].groupby('Значение')[['Акт']].sum().reset_index()
    
    status_fig = go.Figure(data=[go.Pie(labels=status_data['Значение'], values=status_data['Акт'],
                                         hole=0.4, 
                                         marker=dict(colors=['#FFD700', '#1E90FF']),
                                         textinfo='label+percent')])
    
    # Добавляем центральное значение на круговой диаграмме
    status_fig.add_annotation(text=f"Всего актов: {total_acts_count}", 
                              font_size=20, showarrow=False)
    # Изменение размеров диаграммы
    status_fig.update_layout(width=900, height=700, yaxis_title_font=dict(size=14), xaxis_title_font=dict(size=14))

    return yearly_fig, subject_fig, document_fig, status_fig, total_acts_count, active_acts_count, inactive_acts_count, primary_acts_count, amending_acts_count

# Основная часть приложения Streamlit
st.markdown("# Анализ нормативных правовых актов субъектов Российской Федерации")

year_range = st.slider('', min_value=int(df['Год'].min()), max_value=int(df['Год'].max()), value=(int(df['Год'].min()), int(df['Год'].max())))

# Обновляем графики и индикаторы
yearly_fig, subject_fig, document_fig, status_fig, total_acts_count, active_acts_count, inactive_acts_count, primary_acts_count, amending_acts_count = update_charts_and_indicators(year_range)

# Отображаем индикаторы на одной строке
col1, col2, col3, col4, col5 = st.columns(5)

# Функция для отображения метрики с кастомизированным размером текста
def custom_metric(label, value):
    st.markdown(f"<h4 style='font-size: 18px; text-align: left;'>{label}</h4>", unsafe_allow_html=True)  # Измените размер шрифта здесь
    st.metric(label="", value=value)

with col1:
    custom_metric("Общее количество НПА", f"{total_acts_count:,}".replace(",", " "))
with col2:
    custom_metric("Действующие", f"{active_acts_count}%")
with col3:
    custom_metric("Недействующие", f"{inactive_acts_count}%")
with col4:
    custom_metric("Основные", f"{primary_acts_count}%")
with col5:
    custom_metric("Изменяющие", f"{amending_acts_count}%")



# Отображаем графики статусов
col1, col2 = st.columns(2)
with col1:
    # Отображаем графики во всю ширину страницы
    st.plotly_chart(yearly_fig, use_container_width=True)
    st.plotly_chart(document_fig, use_container_width=True)
with col2:
    st.plotly_chart(subject_fig, use_container_width=True)
    st.plotly_chart(status_fig, use_container_width=True) 

   
