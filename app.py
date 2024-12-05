import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from io import BytesIO

# 新增导入
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.utils import ImageReader

# 地中海风格配色方案
COLORS = {
    'background': '#F5F5F0',  # 温暖的米白色背景
    'text': '#2C3E50',        # 深灰偏暖的文字颜色
    'card_bg': 'rgba(255, 255, 255, 0.8)',  # 纯白磨砂玻璃
    'positive': '#7CB342',    # 橄榄绿用于正增长
    'negative': '#E57373',    # 柔和的红色用于负增长
    'chart_colors': [
        '#1E88E5',  # 地中海蓝
        '#90CAF9',  # 浅蓝
        '#7CB342',  # 橄榄绿
        '#FFB74D',  # 温暖的橙色
    ],
    'border': 'rgba(44, 62, 80, 0.1)',  # 柔和的边框色
}

# 语言字典
translations = {
    'zh': {
        'title': "Surfin 2024年学习发展工作培训数据看板",
        'download_pdf': "下载PDF报告",
        'key_metrics': "年度关键指标对比",
        'detailed_comparison': "年度指标详细对比",
        'analysis_title': "培训数据深度分析报告",
        'analysis_content': (
            "基于当前的培训数据分析，我们观察到以下趋势：\n\n"
            "- **总课程数**：{course_trend}\n"
            "- **总参训人次**：{participants_trend}\n"
            "- **总培训时长**：{hours_trend}\n"
            "- **总培训人时**：{person_hours_trend}\n\n"
            "这些变化可能是由于{possible_causes}。\n\n"
            "为了进一步提升培训效果，我们建议{recommendations}。"
        ),
        'trend_increase': "相比去年增长了{value:.1f}%，表明培训课程的数量有所增加",
        'trend_decrease': "相比去年减少了{value:.1f}%，需要关注培训课程的数量下降趋势",
        'trend_no_change': "与去年持平，培训课程数量保持稳定",
        'possible_causes': "业务需求的变化、员工发展计划的调整或培训资源的重新分配",
        'recommendations': "深入分析培训需求，优化培训课程设计，加强培训资源的投入",
        'total_courses': "总课程数",
        'total_participants': "总参训人次",
        'total_training_hours': "总培训时长",
        'total_training_person_hours': "总培训人时",
        'bar_chart': "柱状图",
        'pie_chart': "饼图",
        'radar_chart': "雷达图",
        'year_2023': "2023年",
        'year_2024': "2024年",
        'growth': "同比增长",
        'units': {'total_courses': '门', 'total_participants': '人次', 'total_training_hours': '小时', 'total_training_person_hours': '小时'},
        'metrics': ['total_courses', 'total_participants', 'total_training_hours', 'total_training_person_hours'],
        'metric_labels': {
            'total_courses': "总课程数",
            'total_participants': "总参训人次",
            'total_training_hours': "总培训时长",
            'total_training_person_hours': "总培训人时",
        },
        'data_input': {
            'data_2023': "2023年数据",
            'data_2024': "2024年数据",
        }
    },
    'en': {
        'title': "Surfin 2024 Training Data Dashboard",
        'download_pdf': "Download PDF Report",
        'key_metrics': "Annual Key Metrics Comparison",
        'detailed_comparison': "Detailed Annual Metrics Comparison",
        'analysis_title': "In-depth Training Data Analysis Report",
        'analysis_content': (
            "Based on the current training data analysis, we have observed the following trends:\n\n"
            "- **Total Courses**: {course_trend}\n"
            "- **Total Participants**: {participants_trend}\n"
            "- **Total Training Hours**: {hours_trend}\n"
            "- **Total Training Person-Hours**: {person_hours_trend}\n\n"
            "These changes may be due to {possible_causes}.\n\n"
            "To further enhance training effectiveness, we recommend {recommendations}."
        ),
        'trend_increase': "increased by {value:.1f}% compared to last year, indicating a rise in the number of training courses",
        'trend_decrease': "decreased by {value:.1f}% compared to last year, requiring attention to the downward trend in training courses",
        'trend_no_change': "remained the same as last year, maintaining a stable number of training courses",
        'possible_causes': "changes in business needs, adjustments in employee development plans, or reallocation of training resources",
        'recommendations': "conducting in-depth training needs analysis, optimizing training course design, and enhancing investment in training resources",
        'total_courses': "Total Courses",
        'total_participants': "Total Participants",
        'total_training_hours': "Total Training Hours",
        'total_training_person_hours': "Total Training Person-Hours",
        'bar_chart': "Bar Chart",
        'pie_chart': "Pie Chart",
        'radar_chart': "Radar Chart",
        'year_2023': "Year 2023",
        'year_2024': "Year 2024",
        'growth': "Growth Compared to Last Year",
        'units': {'total_courses': '', 'total_participants': '', 'total_training_hours': 'h', 'total_training_person_hours': 'h'},
        'metrics': ['total_courses', 'total_participants', 'total_training_hours', 'total_training_person_hours'],
        'metric_labels': {
            'total_courses': "Total Courses",
            'total_participants': "Total Participants",
            'total_training_hours': "Total Training Hours",
            'total_training_person_hours': "Total Training Person-Hours",
        },
        'data_input': {
            'data_2023': "Data for 2023",
            'data_2024': "Data for 2024",
        }
    }
}

# 初始数据
data_2023 = {
    'total_courses': 39,
    'total_participants': 445,
    'total_training_hours': 66,
    'total_training_person_hours': 648
}

data_2024 = {
    'total_courses': 24,
    'total_participants': 429,
    'total_training_hours': 57.5,
    'total_training_person_hours': 1036.5
}

def calculate_growth(current, previous):
    return ((current - previous) / previous * 100) if previous != 0 else 0

growth_data = {
    key: calculate_growth(data_2024[key], data_2023[key]) for key in data_2023
}

# 添加全局样式
app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* 您的CSS样式代码 */
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# 创建年度对比卡片
def create_comparison_card(metric_key, value_2024, value_2023, growth, suffix='', lang='zh'):
    translations_lang = translations[lang]
    title = translations_lang['metric_labels'][metric_key]
    growth_label = translations_lang['growth']
    year_2023 = translations_lang['year_2023']
    year_2024 = translations_lang['year_2024']

    growth_color = COLORS['positive'] if growth >= 0 else COLORS['negative']
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className="card-title", style={
                        'color': COLORS['text'],
                        'margin-bottom': '1rem',
                        'font-weight': '500'
                    }),
                    html.Div([
                        html.H2(f"{value_2024}{suffix}", style={
                            'color': COLORS['text'],
                            'margin-bottom': '0.5rem',
                            'font-weight': '600'
                        }),
                        html.P(f"{year_2024}", style={
                            'color': COLORS['text'],
                            'opacity': '0.7',
                            'margin-bottom': '1rem',
                            'font-size': '0.9rem'
                        }),
                        html.Div([
                            html.Span(f"{value_2023}{suffix}", style={
                                'color': COLORS['text'],
                                'opacity': '0.8',
                                'font-weight': '500',
                                'margin-right': '0.5rem'
                            }),
                            html.Small(f"{year_2023}", style={
                                'color': COLORS['text'],
                                'opacity': '0.6'
                            })
                        ]),
                        html.Div([
                            html.Span(
                                f"{'+' if growth > 0 else ''}{growth:.1f}%",
                                style={
                                    'color': growth_color,
                                    'font-weight': '600',
                                    'margin-top': '0.5rem',
                                    'display': 'inline-block',
                                    'padding': '0.25rem 0.75rem',
                                    'border-radius': '1rem',
                                    'background-color': f"rgba({int(growth_color[1:3], 16)}, {int(growth_color[3:5], 16)}, {int(growth_color[5:7], 16)}, 0.1)",
                                }
                            ),
                        ], style={'margin-top': '0.5rem'})
                    ])
                ]
            )
        ],
        style={
            'background-color': COLORS['card_bg'],
            'border': f"1px solid {COLORS['border']}",
            'border-radius': '1rem',
            'overflow': 'hidden',
            'backdrop-filter': 'blur(10px)',
            '-webkit-backdrop-filter': 'blur(10px)',
            'box-shadow': '0 4px 6px rgba(44, 62, 80, 0.05)',
            'transition': 'all 0.3s ease',
            'height': '100%'
        }
    )

# 创建图表类型选择器
def create_chart_type_selector(metric_key, lang='zh'):
    translations_lang = translations[lang]
    return dbc.Select(
        id=f'chart-type-{metric_key}',
        options=[
            {'label': translations_lang['bar_chart'], 'value': 'bar'},
            {'label': translations_lang['pie_chart'], 'value': 'pie'},
            {'label': translations_lang['radar_chart'], 'value': 'radar'},
        ],
        value='bar',
        style={
            'borderRadius': '8px',
            'border': '1px solid rgba(0,0,0,0.1)',
            'backgroundColor': 'rgba(255,255,255,0.8)',
            'backdropFilter': 'blur(10px)',
            '-webkit-backdrop-filter': 'blur(10px)',
            'padding': '8px 12px',
            'fontSize': '14px',
            'marginBottom': '1rem',
            'width': 'auto',
            'color': COLORS['text']
        }
    )

# 创建图表数据
def create_chart_data(metric_key, unit, chart_type='bar', lang='zh'):
    translations_lang = translations[lang]
    metric_label = translations_lang['metric_labels'][metric_key]
    year_2023 = translations_lang['year_2023']
    year_2024 = translations_lang['year_2024']

    fig = go.Figure()
    if chart_type == 'bar':
        fig.add_trace(go.Bar(
            name=year_2023,
            x=[metric_label],
            y=[data_2023[metric_key]],
            marker_color=COLORS['chart_colors'][1],
            hovertemplate=f"%{{y}}{unit}<extra></extra>",
            marker=dict(opacity=0.9)
        ))
        fig.add_trace(go.Bar(
            name=year_2024,
            x=[metric_label],
            y=[data_2024[metric_key]],
            marker_color=COLORS['chart_colors'][0],
            hovertemplate=f"%{{y}}{unit}<extra></extra>",
            marker=dict(opacity=0.9)
        ))
        fig.update_layout(barmode='group')
    elif chart_type == 'pie':
        fig.add_trace(go.Pie(
            values=[data_2023[metric_key], data_2024[metric_key]],
            labels=[year_2023, year_2024],
            hole=0.4,
            marker_colors=[COLORS['chart_colors'][1], COLORS['chart_colors'][0]],
            textinfo='label+percent',
            hovertemplate="%{label}<br>%{value}" + unit + "<br>占比: %{percent}<extra></extra>",
            textfont=dict(
                family='-apple-system, BlinkMacSystemFont, "SF Pro Text"',
                size=14,
                color=COLORS['text']
            ),
        ))
    else:  # radar
        metrics = translations_lang['metrics']
        categories = [translations_lang['metric_labels'][m] for m in metrics]
        values_2023 = [data_2023[m] for m in metrics]
        values_2024 = [data_2024[m] for m in metrics]

        fig.add_trace(go.Scatterpolar(
            r=values_2023,
            theta=categories,
            fill='toself',
            name=year_2023,
            line_color=COLORS['chart_colors'][1],
            hovertemplate="%{theta}<br>%{r}" + "<extra></extra>"
        ))
        fig.add_trace(go.Scatterpolar(
            r=values_2024,
            theta=categories,
            fill='toself',
            name=year_2024,
            line_color=COLORS['chart_colors'][0],
            hovertemplate="%{theta}<br>%{r}" + "<extra></extra>"
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    showticklabels=False,
                    gridcolor='rgba(0,0,0,0.1)',
                ),
                angularaxis=dict(
                    gridcolor='rgba(0,0,0,0.1)',
                    linecolor='rgba(0,0,0,0.1)',
                )
            )
        )

    # 通用布局设置
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(
            text=f'{metric_label} {translations_lang["detailed_comparison"]} (单位: {unit})',
            font=dict(
                size=16,
                color=COLORS['text'],
                family='-apple-system, BlinkMacSystemFont, "SF Pro Text"'
            )
        ),
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                family='-apple-system, BlinkMacSystemFont, "SF Pro Text"',
                size=12,
                color=COLORS['text']
            ),
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='rgba(255,255,255,0.4)',
            borderwidth=1
        ),
        height=300,
        hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_family='-apple-system, BlinkMacSystemFont, "SF Pro Text"'
        ),
    )

    if chart_type == 'bar':
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linecolor='rgba(0,0,0,0.1)',
            tickfont=dict(
                family='-apple-system, BlinkMacSystemFont, "SF Pro Text"',
                size=12,
                color=COLORS['text']
            )
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.05)',
            tickfont=dict(
                family='-apple-system, BlinkMacSystemFont, "SF Pro Text"',
                size=12,
                color=COLORS['text']
            )
        )
    return fig

def serve_layout():
    return dbc.Container([
        # 存储当前语言
        dcc.Store(id='language-store', data='zh'),
        # 存储数据
        dcc.Store(id='data-2023-store', data=data_2023),
        dcc.Store(id='data-2024-store', data=data_2024),
        
        # 语言切换按钮
        html.Div([
            dbc.Button("EN", id="language-button", color="secondary", size="sm", outline=True, style={
                'position': 'absolute',
                'top': '20px',
                'right': '20px',
                'borderColor': COLORS['text'],
                'color': COLORS['text'],
            })
        ]),
        
        # 标题
        html.H1(id='page-title',
                className="text-center",
                style={'marginBottom': '2rem'}),
        
        # 手动输入组件容器（内容将在回调中更新）
        html.Div(id='input-container'),
        
        # 下载按钮
        html.Div([
            dbc.Button(id="download-pdf-button", color="primary", className="mr-2", style={
                'marginBottom': '2rem',
                'backgroundColor': COLORS['chart_colors'][0],
                'borderColor': COLORS['chart_colors'][0],
                'color': 'white'
            }),
            dcc.Download(id="download-pdf")
        ], style={'textAlign': 'center'}),
        
        # 年度对比指标标题
        html.H4(id='key-metrics-title'),
        
        # 指标卡片
        dbc.Row(id='cards-container', className="g-4"),
        
        # 图表标题
        html.H4(id='detailed-comparison-title', className="mt-4"),
        
        # 图表
        dbc.Row(id='charts-container', className="g-4"),
        
        # 分析标题
        html.H4(id='analysis-title', className="mt-4"),
        
        # 分析内容
        html.Div(id='analysis-content', style={
            'background-color': COLORS['card_bg'],
            'padding': '2rem',
            'border-radius': '1rem',
            'margin-bottom': '2rem',
            'color': COLORS['text'],
            'box-shadow': '0 4px 6px rgba(44, 62, 80, 0.05)',
            'border': f"1px solid {COLORS['border']}",
        }),
        
    ], fluid=True)

app.layout = serve_layout

# 生成分析内容
def generate_analysis(lang):
    translations_lang = translations[lang]
    year_2023 = translations_lang['year_2023']
    year_2024 = translations_lang['year_2024']
    analysis_template = translations_lang['analysis_content']
    trend_increase = translations_lang['trend_increase']
    trend_decrease = translations_lang['trend_decrease']
    trend_no_change = translations_lang['trend_no_change']
    possible_causes = translations_lang['possible_causes']
    recommendations = translations_lang['recommendations']
    metrics = translations_lang['metrics']
    metric_labels = translations_lang['metric_labels']
    
    trends = {}
    for metric in metrics:
        growth = growth_data[metric]
        if growth > 0:
            trend_text = trend_increase.format(value=abs(growth))
        elif growth < 0:
            trend_text = trend_decrease.format(value=abs(growth))
        else:
            trend_text = trend_no_change
        trends[metric + '_trend'] = trend_text
    
    analysis_text = analysis_template.format(
        course_trend=trends['total_courses_trend'],
        participants_trend=trends['total_participants_trend'],
        hours_trend=trends['total_training_hours_trend'],
        person_hours_trend=trends['total_training_person_hours_trend'],
        possible_causes=possible_causes,
        recommendations=recommendations
    )
    
    # 使用卡片式布局和图标
    analysis_card = dbc.Card(
        dbc.CardBody([
            html.P(analysis_text, style={'whiteSpace': 'pre-line', 'fontSize': '1rem'}),
        ]),
        style={
            'background-color': COLORS['card_bg'],
            'border': f"1px solid {COLORS['border']}",
            'border-radius': '1rem',
            'box-shadow': '0 4px 6px rgba(44, 62, 80, 0.05)',
            'color': COLORS['text'],
        }
    )
    
    return analysis_card

# 更新页面内容的回调函数
@app.callback(
    Output('page-title', 'children'),
    Output('download-pdf-button', 'children'),
    Output('key-metrics-title', 'children'),
    Output('detailed-comparison-title', 'children'),
    Output('language-button', 'children'),
    Output('cards-container', 'children'),
    Output('charts-container', 'children'),
    Output('input-container', 'children'),
    Output('analysis-title', 'children'),
    Output('analysis-content', 'children'),
    Input('language-store', 'data'),
    Input('data-2023-store', 'data'),
    Input('data-2024-store', 'data'),
)
def update_content(lang, data_2023_store, data_2024_store):
    global data_2023, data_2024, growth_data
    data_2023 = data_2023_store
    data_2024 = data_2024_store
    growth_data = {
        key: calculate_growth(data_2024[key], data_2023[key]) for key in data_2023
    }
    translations_lang = translations[lang]
    metrics = translations_lang['metrics']
    units = translations_lang['units']
    metric_labels = translations_lang['metric_labels']
    
    # 更新按钮文字
    language_button_text = 'EN' if lang == 'zh' else '中文'
    
    # 创建手动输入组件
    data_input_labels = translations_lang['data_input']
    input_components = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label(data_input_labels['data_2023'], style={'fontWeight': 'bold'}),
                *[
                    dbc.InputGroup([
                        dbc.InputGroupText(metric_labels[metric]),
                        dbc.Input(id=f'input-2023-{metric}', type='number', value=data_2023[metric]),
                    ], className='mb-2')
                    for metric in metrics
                ],
            ], width=6),
            dbc.Col([
                dbc.Label(data_input_labels['data_2024'], style={'fontWeight': 'bold'}),
                *[
                    dbc.InputGroup([
                        dbc.InputGroupText(metric_labels[metric]),
                        dbc.Input(id=f'input-2024-{metric}', type='number', value=data_2024[metric]),
                    ], className='mb-2')
                    for metric in metrics
                ],
            ], width=6),
        ], className='mb-4'),
    ])
    
    # 创建指标卡片
    cards = [
        dbc.Col(create_comparison_card(metric, data_2024[metric], data_2023[metric],
                                       growth_data[metric], units[metric], lang=lang), width=12, lg=3, className='mb-4')
        for metric in metrics
    ]
    
    # 创建图表
    charts = [
        dbc.Col([
            html.Div([
                create_chart_type_selector(metric, lang=lang),
                dcc.Graph(
                    id=f'chart-{metric}',
                    figure=create_chart_data(metric, units[metric], lang=lang),
                    config={'displayModeBar': False}
                )
            ], className='chart-container')
        ], width=12, lg=6)
        for metric in metrics
    ]
    
    # 更新下载按钮文字
    download_button_text = translations_lang['download_pdf']
    
    # 生成分析内容
    analysis_title = translations_lang['analysis_title']
    analysis_content = generate_analysis(lang)
    
    return (translations_lang['title'],
            download_button_text,
            translations_lang['key_metrics'],
            translations_lang['detailed_comparison'],
            language_button_text,
            cards,
            charts,
            input_components,
            analysis_title,
            analysis_content)

# 切换语言的回调函数
@app.callback(
    Output('language-store', 'data'),
    Input('language-button', 'n_clicks'),
    State('language-store', 'data')
)
def switch_language(n_clicks, lang):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    return 'en' if lang == 'zh' else 'zh'

# 回调函数：更新图表类型
def generate_update_chart(metric_key):
    @app.callback(
        Output(f'chart-{metric_key}', 'figure'),
        Input(f'chart-type-{metric_key}', 'value'),
        Input('language-store', 'data'),
        Input('data-2023-store', 'data'),
        Input('data-2024-store', 'data'),
    )
    def update_chart(chart_type, lang, data_2023_store, data_2024_store):
        global data_2023, data_2024
        data_2023 = data_2023_store
        data_2024 = data_2024_store
        translations_lang = translations[lang]
        units = translations_lang['units']
        return create_chart_data(metric_key, units[metric_key], chart_type, lang=lang)
    return update_chart

for metric in ['total_courses', 'total_participants', 'total_training_hours', 'total_training_person_hours']:
    generate_update_chart(metric)

# 回调函数：更新数据存储
@app.callback(
    Output('data-2023-store', 'data'),
    Output('data-2024-store', 'data'),
    Input('input-2023-total_courses', 'value'),
    Input('input-2023-total_participants', 'value'),
    Input('input-2023-total_training_hours', 'value'),
    Input('input-2023-total_training_person_hours', 'value'),
    Input('input-2024-total_courses', 'value'),
    Input('input-2024-total_participants', 'value'),
    Input('input-2024-total_training_hours', 'value'),
    Input('input-2024-total_training_person_hours', 'value'),
    State('data-2023-store', 'data'),
    State('data-2024-store', 'data'),
)
def update_data_manual(
    input_2023_total_courses, input_2023_total_participants,
    input_2023_total_training_hours, input_2023_total_training_person_hours,
    input_2024_total_courses, input_2024_total_participants,
    input_2024_total_training_hours, input_2024_total_training_person_hours,
    data_2023_store, data_2024_store
):
    data_2023 = data_2023_store.copy()
    data_2024 = data_2024_store.copy()
    data_2023['total_courses'] = input_2023_total_courses or 0
    data_2023['total_participants'] = input_2023_total_participants or 0
    data_2023['total_training_hours'] = input_2023_total_training_hours or 0
    data_2023['total_training_person_hours'] = input_2023_total_training_person_hours or 0
    data_2024['total_courses'] = input_2024_total_courses or 0
    data_2024['total_participants'] = input_2024_total_participants or 0
    data_2024['total_training_hours'] = input_2024_total_training_hours or 0
    data_2024['total_training_person_hours'] = input_2024_total_training_person_hours or 0
    return data_2023, data_2024

# 回调函数：生成并下载PDF
@app.callback(
    Output("download-pdf", "data"),
    Input("download-pdf-button", "n_clicks"),
    State('language-store', 'data'),
    State('data-2023-store', 'data'),
    State('data-2024-store', 'data'),
    prevent_initial_call=True,
)
def generate_pdf(n_clicks, lang, data_2023_store, data_2024_store):
    try:
        data_2023 = data_2023_store
        data_2024 = data_2024_store
        growth_data = {
            key: calculate_growth(data_2024[key], data_2023[key]) for key in data_2023
        }
        translations_lang = translations[lang]
        metrics = translations_lang['metrics']
        units_dict = translations_lang['units']
        title = translations_lang['title']
        year_2023 = translations_lang['year_2023']
        year_2024 = translations_lang['year_2024']
        growth_label = translations_lang['growth']
        metric_labels = translations_lang['metric_labels']
        
        # 创建PDF缓冲区
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # 使用内置字体
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        p.setFont("STSong-Light", 16)
        p.drawString(100, 750, title)
        
        # 绘制2023年数据
        y = 700
        p.setFont("STSong-Light", 12)
        p.drawString(50, y, f"{year_2023}{translations_lang['key_metrics']}:")
        y -= 20
        for key in metrics:
            value = data_2023[key]
            label = metric_labels[key]
            p.drawString(60, y, f"{label}: {value}{units_dict[key]}")
            y -= 15
        
        # 绘制2024年数据
        y -= 10
        p.drawString(50, y, f"{year_2024}{translations_lang['key_metrics']}:")
        y -= 20
        for key in metrics:
            value = data_2024[key]
            label = metric_labels[key]
            p.drawString(60, y, f"{label}: {value}{units_dict[key]}")
            y -= 15
        
        # 绘制增长率
        y -= 10
        p.drawString(50, y, f"{growth_label}:")
        y -= 20
        for key in metrics:
            value = growth_data[key]
            label = metric_labels[key]
            growth_text = f"{'+' if value > 0 else ''}{value:.1f}%"
            p.drawString(60, y, f"{label}: {growth_text}")
            y -= 15
        
        # 绘制分析内容
        y -= 20
        p.setFont("STSong-Light", 14)
        p.drawString(50, y, translations_lang['analysis_title'])
        y -= 20
        p.setFont("STSong-Light", 12)
        analysis_content = generate_analysis(lang)
        # 获取分析文本
        analysis_text = analysis_content.children[0].children
        text_lines = analysis_text.split('\n')
        for line in text_lines:
            p.drawString(60, y, line)
            y -= 15
            if y < 100:
                p.showPage()
                y = 750
                p.setFont("STSong-Light", 12)
        
        # 插入图表
        y -= 30  # 调整位置
        
        for metric in metrics:
            if y < 300:
                p.showPage()
                y = 750
                p.setFont("STSong-Light", 12)
            
            # 生成图表
            fig = create_chart_data(metric, units_dict[metric], chart_type='bar', lang=lang)
            
            # 将图表保存为图像
            img_bytes = fig.to_image(format="png", engine='kaleido')
            img_buffer = BytesIO(img_bytes)
            img_buffer.seek(0)
            
            # 将图像插入PDF
            img = ImageReader(img_buffer)
            p.drawImage(img, 50, y - 250, width=500, height=250)
            y -= 270  # 调整y位置
        
        # 完成PDF绘制
        p.save()
        buffer.seek(0)
        filename = "数据报告.pdf" if lang == 'zh' else "Data_Report.pdf"
        return dcc.send_bytes(buffer.getvalue(), filename=filename)
    except Exception as e:
        print(f"PDF生成错误: {e}")
        return

if __name__ == '__main__':
    app.run_server(host='localhost', port=8050, debug=True)
