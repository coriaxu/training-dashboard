import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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

# 2023年数据
data_2023 = {
    '总课程数': 39,
    '总参训人次': 445,
    '总培训时长': 66,
    '总培训人时': 648
}

# 2024年数据
data_2024 = {
    '总课程数': 24,
    '总参训人次': 429,
    '总培训时长': 57.5,
    '总培训人时': 1036.5
}

# 计算同比增长
def calculate_growth(current, previous):
    return ((current - previous) / previous * 100) if previous != 0 else 0

growth_data = {
    '总课程数': calculate_growth(data_2024['总课程数'], data_2023['总课程数']),
    '总参训人次': calculate_growth(data_2024['总参训人次'], data_2023['总参训人次']),
    '总培训时长': calculate_growth(data_2024['总培训时长'], data_2023['总培训时长']),
    '总培训人时': calculate_growth(data_2024['总培训人时'], data_2023['总培训人时'])
}

# 添加全局样式
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                compress=True)  # 启用压缩
server = app.server  # 添加这行，Vercel 需要它

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: ''' + COLORS['background'] + ''';
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                line-height: 1.5;
                letter-spacing: -0.022em;
            }
            .container-fluid {
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }
            .card {
                backdrop-filter: blur(25px) saturate(180%);
                -webkit-backdrop-filter: blur(25px) saturate(180%);
                background-color: ''' + COLORS['card_bg'] + ''';
                border: none;
                border-radius: 12px;
                box-shadow: 
                    0 2px 5px rgba(0,0,0,0.05),
                    0 0 0 1px rgba(255,255,255,0.4) inset,
                    0 0 0 1px rgba(0,0,0,0.03);
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                padding: 1.5rem;
                position: relative;
                overflow: hidden;
            }
            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(180deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 100%);
                opacity: 0;
                transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .card:hover {
                transform: translateY(-2px) scale(1.005);
                box-shadow: 
                    0 8px 20px rgba(0,0,0,0.08),
                    0 0 0 1px rgba(255,255,255,0.5) inset,
                    0 0 0 1px rgba(0,0,0,0.03);
                background-color: ''' + COLORS['card_bg'] + ''';
            }
            .card:hover::before {
                opacity: 1;
            }
            .metric-value {
                font-weight: 600;
                letter-spacing: -0.025em;
                font-size: 1.75rem;
                margin: 0;
                line-height: 1.2;
                background: linear-gradient(135deg, ''' + COLORS['text'] + ''' 0%, #434344 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .metric-title {
                color: ''' + COLORS['text'] + ''';
                font-size: 0.95rem;
                font-weight: 500;
                margin-bottom: 1rem;
                letter-spacing: -0.01em;
            }
            .growth-indicator {
                font-size: 0.875rem;
                font-weight: 500;
                padding: 4px 10px;
                border-radius: 8px;
                margin-left: 8px;
                display: inline-flex;
                align-items: center;
                line-height: 1;
                transition: all 0.3s ease;
            }
            .growth-indicator:hover {
                transform: scale(1.05);
            }
            h1, h4 {
                font-weight: 600;
                letter-spacing: -0.025em;
            }
            h1 {
                font-size: 2.25rem;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, ''' + COLORS['text'] + ''' 0%, #434344 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            h4 {
                font-size: 1.25rem;
                margin-bottom: 1.5rem;
                color: ''' + COLORS['text'] + ''';
            }
            .chart-container {
                background: rgba(255,255,255,0.7);
                backdrop-filter: blur(25px) saturate(180%);
                -webkit-backdrop-filter: blur(25px) saturate(180%);
                border-radius: 12px;
                padding: 1.25rem;
                box-shadow: 
                    0 2px 5px rgba(0,0,0,0.05),
                    0 0 0 1px rgba(255,255,255,0.4) inset,
                    0 0 0 1px rgba(0,0,0,0.03);
                margin-bottom: 1.5rem;
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .chart-container:hover {
                transform: translateY(-2px);
                box-shadow: 
                    0 8px 20px rgba(0,0,0,0.08),
                    0 0 0 1px rgba(255,255,255,0.5) inset,
                    0 0 0 1px rgba(0,0,0,0.03);
            }
            @media (max-width: 768px) {
                .container-fluid {
                    padding: 1rem;
                }
                h1 {
                    font-size: 1.75rem;
                    margin-bottom: 1.5rem;
                }
                h4 {
                    font-size: 1.125rem;
                    margin-bottom: 1rem;
                }
                .metric-value {
                    font-size: 1.5rem;
                }
                .card {
                    padding: 1.25rem;
                }
            }
            .modebar {
                display: none !important;
            }
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
def create_comparison_card(title, value_2024, value_2023, growth, suffix=''):
    growth_color = COLORS['positive'] if growth >= 0 else COLORS['negative']
    growth_icon = '↑' if growth >= 0 else '↓'
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
                        html.P(f"2024年", style={
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
                            html.Small("2023年", style={
                                'color': COLORS['text'],
                                'opacity': '0.6'
                            })
                        ]),
                        html.Div([
                            html.Span(
                                f"{'+' if growth > 0 else ''}{growth:.1f}%",
                                style={
                                    'color': COLORS['positive'] if growth > 0 else COLORS['negative'],
                                    'font-weight': '600',
                                    'margin-top': '0.5rem',
                                    'display': 'inline-block',
                                    'padding': '0.25rem 0.75rem',
                                    'border-radius': '1rem',
                                    'background-color': f"{'rgba(124, 179, 66, 0.1)' if growth > 0 else 'rgba(229, 115, 115, 0.1)'}",
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
def create_chart_type_selector(metric):
    return dbc.Select(
        id=f'chart-type-{metric}',
        options=[
            {'label': '柱状图', 'value': 'bar'},
            {'label': '饼图', 'value': 'pie'},
            {'label': '雷达图', 'value': 'radar'},
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

# 创建图表
def create_year_comparison_charts():
    metrics = ['总课程数', '总参训人次', '总培训时长', '总培训人时']
    units = ['门', '人次', '小时', '小时']
    return [{'metric': metric, 'unit': unit} for metric, unit in zip(metrics, units)]

def create_chart_data(metric, unit, chart_type='bar'):
    fig = px.bar(x=[metric], y=[data_2023[metric], data_2024[metric]], color_discrete_sequence=[COLORS['chart_colors'][1], COLORS['chart_colors'][0]], barmode='group') if chart_type == 'bar' else px.pie(values=[data_2023[metric], data_2024[metric]], names=['2023年', '2024年'], color_discrete_sequence=[COLORS['chart_colors'][1], COLORS['chart_colors'][0]]) if chart_type == 'pie' else px.scatter_polar(r=[data_2023[metric], data_2024[metric]], theta=['2023年', '2024年'], color_discrete_sequence=[COLORS['chart_colors'][1], COLORS['chart_colors'][0]])
    
    # 通用布局设置
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(
            text=f'{metric}对比 (单位: {unit})',
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
    
    return fig

# 应用布局
def serve_layout():
    metrics = ['总课程数', '总参训人次', '总培训时长', '总培训人时']
    units = ['门', '人次', '小时', '小时']
    
    return dbc.Container([
        # 标题
        html.H1("Surfin2024年学习发展工作培训数据看板", 
                className="text-center", 
                style={'marginBottom': '2rem'}),
        
        # 年度对比指标
        html.H4("年度关键指标对比"),
        
        # 指标卡片
        dbc.Row([
            dbc.Col(create_comparison_card("总课程数", data_2024['总课程数'], data_2023['总课程数'], 
                                         growth_data['总课程数'], "门"), width=12, lg=3, className='mb-4'),
            dbc.Col(create_comparison_card("总参训人次", data_2024['总参训人次'], data_2023['总参训人次'], 
                                         growth_data['总参训人次'], "人"), width=12, lg=3, className='mb-4'),
            dbc.Col(create_comparison_card("总培训时长", data_2024['总培训时长'], data_2023['总培训时长'], 
                                         growth_data['总培训时长'], "小时"), width=12, lg=3, className='mb-4'),
            dbc.Col(create_comparison_card("总培训人时", data_2024['总培训人时'], data_2023['总培训人时'], 
                                         growth_data['总培训人时'], "小时"), width=12, lg=3, className='mb-4'),
        ], className="g-4"),
        
        # 图表标题
        html.H4("年度指标详细对比", className="mt-4"),
        
        # 图表
        dbc.Row([
            dbc.Col([
                html.Div([
                    create_chart_type_selector(metric),
                    dcc.Graph(
                        id=f'chart-{metric}',
                        figure=create_chart_data(metric, unit),
                        config={'displayModeBar': False}
                    )
                ], className='chart-container')
            ], width=12, lg=6) 
            for metric, unit in zip(metrics, units)
        ], className="g-4"),
        
    ], fluid=True)

app.layout = serve_layout

# 回调函数：更新图表类型
for metric in ['总课程数', '总参训人次', '总培训时长', '总培训人时']:
    @app.callback(
        dash.dependencies.Output(f'chart-{metric}', 'figure'),
        dash.dependencies.Input(f'chart-type-{metric}', 'value')
    )
    def update_chart(chart_type, metric=metric):
        units = {'总课程数': '门', '总参训人次': '人次', '总培训时长': '小时', '总培训人时': '小时'}
        return create_chart_data(metric, units[metric], chart_type)

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
