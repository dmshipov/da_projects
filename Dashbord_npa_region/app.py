
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Чтение данных из Excel-файла
df = pd.read_excel('result.xlsx')


# Инициализация приложения Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Анализ нормативных правовых актов субъектов Российской Федерации'),
    html.Div(className="indicators", children=[
        html.Div(className="indicator-item", style={"display": "flex", "align-items": "center"}, children=[
            html.H4("Всего НПА:", style={"color": "#4A4A4A", "font-family": "Arial, sans-serif"}), 
            html.P(id="total-acts-count", style={"margin-left": "10px", "font-weight": "bold", "font-size": "20px"})
        ]),
        html.Div(className="indicator-item", style={"display": "flex", "align-items": "center"}, children=[
            html.H4("Действующих:", style={"color": "#4A4A4A", "font-family": "Arial, sans-serif"}),
            html.P(id="active-acts-count", style={"margin-left": "10px", "font-weight": "bold", "font-size": "20px"})
        ]),
        html.Div(className="indicator-item", style={"display": "flex", "align-items": "center"}, children=[
            html.H4("Не действующих:", style={"color": "#4A4A4A", "font-family": "Arial, sans-serif"}),
            html.P(id="inactive-acts-count", style={"margin-left": "10px", "font-weight": "bold", "font-size": "20px"})
        ]),
        html.Div(className="indicator-item", style={"display": "flex", "align-items": "center"}, children=[
            html.H4("Основных:", style={"color": "#4A4A4A", "font-family": "Arial, sans-serif"}),
            html.P(id="primary-acts-count", style={"margin-left": "10px", "font-weight": "bold", "font-size": "20px"})
        ]),
        html.Div(className="indicator-item", style={"display": "flex", "align-items": "center"}, children=[
            html.H4("Изменяющих:", style={"color": "#4A4A4A", "font-family": "Arial, sans-serif"}),
            html.P(id="amending-acts-count", style={"margin-left": "10px", "font-weight": "bold", "font-size": "20px"})
        ])
    ], style={"display": "flex", "gap": "20px", "flex-wrap": "wrap", "background": "linear-gradient(to right, #f0f0f0, #ffffff)", "border-radius": "10px", "padding": "20px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}),
    
    
   
    html.Div([
        dcc.RangeSlider(
            id='year-slider',
            min=df["Год"].min(),
            max=df["Год"].max(),
            value=[df["Год"].min(), df["Год"].max()],
            marks={int(year): str(year) for year in range(df["Год"].min(), df["Год"].max() + 1)},
            step=None,
            allowCross=False
        ),
    ], style={"margin": "20px"}),

    html.Div([
        dcc.Graph(id='yearly-acts', style={'width': '53%', 'height': '37vh'}),
        dcc.Graph(id='acts-by-subject', style={'width': '47%', 'height': '37vh'}, config={'scrollZoom': False},
        )
        
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
    html.Div([
        dcc.Graph(id='acts-by-status', style={'width': '50%', 'height': '42vh'}),
        dcc.Graph(id='acts-by-document', style={'width': '47%', 'height': '42vh'})
    ], style={'display': 'flex', 'justify-content': 'space-between'})
], style={"font-family": "Arial"})

@app.callback(
    [
        Output('total-acts-count', 'children'),
        Output('active-acts-count', 'children'),
        Output('inactive-acts-count', 'children'),
        Output('primary-acts-count', 'children'),
        Output('amending-acts-count', 'children'),
        Output('yearly-acts', 'figure'),
        Output('acts-by-subject', 'figure'),
        Output('acts-by-document', 'figure'),
        Output('acts-by-status', 'figure')
    ],
    Input('year-slider', 'value')
)


def update_charts_and_indicators(selected_years):  # Добавлен новый аргумент
    start_year, end_year = selected_years
    filtered_df = df.query(f'Год >= {start_year} & Год <= {end_year}')
    total_acts_count = filtered_df[filtered_df['Категория'] == 'Вид документа']
    total_acts_count = total_acts_count['Акт'].sum()
    active_acts_count = filtered_df[filtered_df['Значение'] == 'Действующий'] 
    active_acts_count = round(active_acts_count['Акт'].sum() / total_acts_count * 100)
    active_acts_count = f"{active_acts_count}%"
    
    inactive_acts_count = filtered_df[filtered_df['Значение'] == 'Недействующий'] 
    inactive_acts_count = round(inactive_acts_count['Акт'].sum() / total_acts_count * 100)
    inactive_acts_count = f"{inactive_acts_count}%"
    
    primary_acts_count = filtered_df[filtered_df['Значение'] == 'Основной'] 
    primary_acts_count = round(primary_acts_count['Акт'].sum() / total_acts_count * 100)
    primary_acts_count = f"{primary_acts_count}%"
    amending_acts_count = filtered_df[filtered_df['Значение'] == 'Изменяющий'] 
    amending_acts_count = round(amending_acts_count['Акт'].sum() / total_acts_count * 100)
    amending_acts_count = f"{amending_acts_count}%"

    # Акт в динамике по годам
    yearly_data = filtered_df[filtered_df['Категория'] == 'Вид документа']
    yearly_data = yearly_data.groupby('Год')['Акт'].sum().reset_index()

    # Заполняем пропущенные годы значениями 0
    index = pd.Index(range(start_year, end_year + 1), name='Год')
    yearly_data = yearly_data.set_index('Год').reindex(index, fill_value=0).reset_index()
    
    yearly_fig = px.line(yearly_data, x='Год', y='Акт', title='<b>Общее количество НПА субъектов РФ по годам</b>')
    # Настройка оси X для более частых подписей
    yearly_fig.update_xaxes(
        tickvals=yearly_data['Год'],  # Устанавливаем значения для подписей
        dtick=1,  # Шаг между подписями 1 год
        tickangle=0  # Угол наклона подписей для лучшей читаемости
    )
    # Изменяем название оси Y
    yearly_fig.update_layout(
        yaxis_title='Количество НПА субъектов РФ', yaxis=dict(fixedrange=True), height=630# Меняем название оси Y
    )
    # Акт по Субъектам РФ
    subj_data = filtered_df[filtered_df['Категория'] == 'Субъект РФ'].groupby('Федеральный округ')[['Акт']].sum().reset_index().sort_values(by='Акт', ascending=True)
    subj_data['Форматированный акт'] = subj_data['Акт'].apply(lambda x: f"{x:,}".replace(",", " "))
    subject_fig = go.Figure(data=[go.Bar(x=subj_data['Акт'], y=subj_data['Федеральный округ'], orientation='h', text=subj_data['Акт'])])
    subject_fig.update_traces(texttemplate='%{text}', textposition='outside')
    subject_fig.update_layout(title='<b>Количество НПА субъектов РФ по федеральным округам</b>', yaxis_title='Федеральный округ', xaxis_title='Количество НПА субъектов РФ', yaxis=dict(fixedrange=True), height=630)   
    # Акт по Вид документа
    doc_data = filtered_df[filtered_df['Категория'] == 'Вид документа'].groupby(['Значение'])['Акт'].sum().reset_index().sort_values(by='Акт', ascending=False).head(6)
    
    document_fig = go.Figure(data=[go.Bar(x=doc_data['Значение'], y=doc_data['Акт'], orientation='v', text=doc_data['Акт'], marker = dict(color='green'
    ))])
    document_fig.update_traces(texttemplate='%{text}', textposition='outside')
    document_fig.update_layout(title='<b>Количество НПА субъектов РФ по видам документа</b>', yaxis_title='Количество НПА субъектов РФ', xaxis_title='Вид НПА субъекта РФ', xaxis=dict(fixedrange=True), height=630)



    # Акт по Статусу действия документа
    status_data = filtered_df[filtered_df['Категория'] == 'Статус действия документа'].groupby('Значение')[['Акт']].sum().reset_index()

    # Считаем проценты
    total_sum = yearly_data['Акт'].sum()
    status_data['Процент'] = status_data['Акт'].apply(lambda x: round((x / total_sum) * 100, 0))
    status_data = status_data.sort_values(by='Акт', ascending=False).head(2)
    # Строим круговую диаграмму
    status_fig = px.pie(status_data, values='Акт', names='Значение', title='<b>Статусу действия НПА субъектов РФ</b>', hover_data=['Процент'])
    status_fig.update_traces(textinfo='label+percent', textposition='outside', hole=.4)

    # Добавляем аннотацию с общим количеством НПА в центр круга
    status_fig.add_annotation(dict(font=dict(size=14), x=0.5, y=0.5, showarrow=False, text=f'Всего НПА:<br>{total_sum:,}'.replace(',', ' ')))
    # Настройка шрифта легенды и текста
    status_fig.update_layout(
        legend=dict(font=dict(size=14)),  # Увеличиваем размер шрифта легенды
        font=dict(size=14), # Устанавливаем размер шрифта для заголовка
        title_font_size=16,  # Увеличиваем размер шрифта основной надписи               
        height=720
    )

    return (
        f"{total_acts_count:,}".replace(',', ' '),
        f"{active_acts_count}",
        f"{inactive_acts_count}",
        f"{primary_acts_count}",
        f"{amending_acts_count}",
        yearly_fig,
        subject_fig,
        document_fig,
        status_fig
    )

if __name__ == '__main__':
    app.run_server(debug=True)
