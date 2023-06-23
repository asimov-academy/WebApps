from dash import dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from menu_styles import *
from functions import *
from app import *


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line_graph', config={"displayModeBar": False, "showTips": False}, className='graph_line')    
            ], xs=12, md=12,)
    ])
], fluid=True)

# =========  Callbacks  =========== #
# callback line graph
@app.callback(
    Output('line_graph', 'figure'),
    Input('dropdown_card1', 'value'),
    Input('period_input', 'value'),
    Input('profit_switch', 'value'),
    Input('book_data_store', 'data'),
    State('historical_data_store', 'data'),
)
def line_graph(dropdown, period, profit_switch, book_info, historical_info):
    if dropdown == None:
        return no_update
    if type(dropdown) != list: dropdown = [dropdown]
    dropdown = ['IBOV'] + dropdown

    df_hist = pd.DataFrame(historical_info)
    df_hist['datetime'] = pd.to_datetime(df_hist['datetime'], format='%Y-%m-%d %H:%M:%S')
    df_hist = slice_df_timedeltas(df_hist, period)

    fig = go.Figure()

    if profit_switch:
        df_hist = df_hist[df_hist['symbol'].str.contains('|'.join(dropdown))]
        for n, ticker in enumerate(dropdown):
            df_aux = df_hist[df_hist.symbol.str.contains(ticker)]
            df_aux.dropna(inplace=True)
            df_aux.close = df_aux.close / df_aux.close.iloc[0] - 1
            fig.add_trace(go.Scatter(x=df_aux.datetime, y=df_aux.close*100, mode='lines', name=ticker, line=dict(color=LISTA_DE_CORES_LINHAS[n])))
        
    else:
        df_book = pd.DataFrame(book_info)  
        df_patrimonio = definir_evolucao_patrimonial(df_hist, df_book)

        df_ibov = df_hist[df_hist.symbol.str.contains('IBOV')]
        df_ibov.dropna(inplace=True)
        df_ibov.close = df_ibov.close / df_ibov.close.iloc[0] - 1
        fig.add_trace(go.Scatter(x=df_ibov.datetime, y=df_ibov.close*100, mode='lines', name='IBOV', line=dict(color=LISTA_DE_CORES_LINHAS[1])))

        fig.add_trace(go.Scatter(x=df_patrimonio.index, y=(df_patrimonio['evolucao_cum']- 1) * 100, mode='lines', name='Evolução Patrimonial', line=dict(color=LINHA_EVOLUCAO_PATRIMONIAL)))
    
    fig.update_layout(MAIN_CONFIG_2, showlegend=True, yaxis={'ticksuffix': '%'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
    fig.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
    fig.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
    
    return fig

# callback para atulizar o dropdown
@app.callback(
    Output('dropdown_card1', 'value'),
    Output('dropdown_card1', 'options'),
    Input('book_data_store', 'data'),
)
def update_dropdown(book):
    df = pd.DataFrame(book)
    unique = df['ativo'].unique()
    try:
       dropdown = [unique[0], [{'label': x, 'value': x} for x in unique]]
    except:
        dropdown = ['', [{'label': x, 'value': x} for x in unique]]
    
    return dropdown