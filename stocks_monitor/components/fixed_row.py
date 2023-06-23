from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

from menu_styles import *
from functions import *
from app import *

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([html.Img(src='assets/logo_dark.png', height="65px"), "  Stocks Monitor"], className='textoPrincipal'),
                            ])
                        ])
                    ],className='card1_linha1')
                ], xs=12, md=7),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('CARTEIRA:', className='textoSecundario')
                                ], md=4, xs=3, style={'text-align': 'right'}),
                                dbc.Col([
                                    
                                ], md=5, xs=6, id='carteira_valor', style={'text-align': 'left'}),
                                dbc.Col([
                                    
                                ], md=3, xs=3, id='carteira_percent', style={'text-align': 'left'})
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('IBOV: ', className='textoQuartenario')
                                ], md=4, xs=3, style={'text-align': 'right'}),
                                dbc.Col([
                                    
                                ], md=5, xs=5, id='ibov_valor', style={'text-align': 'left'}),
                                dbc.Col([
    
                                ], md=3, xs=4, id='ibov_percent', style={'text-align': 'left'})
                            ])
                        ])
                    ],className='card2_linha1')
                ], md=5, xs=12)
            ],  className='g-2 my-auto'),

            dbc.Row([
                dbc.Col([
                    
                ],md=12, id='cards_ativos'),
            ],  className='g-2 my-auto')
        ], xs=12, md=9),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Switch(id='radar_switch', value=True, label="Setores IBOV X Carteira", className='textoTerciario'),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='radar_graph', config={"displayModeBar": False, "showTips": False})
                        ])
                    ])
                ])
            ], className='cardRadar')
        ], xs=12, md=3),
    ],  className='g-2 my-auto'),
    
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdown_card1', value=[], multi=True, options=[]),
                ], sm=12, md=3),
                dbc.Col([
                    dbc.RadioItems(
                        options=[{'label': x, 'value': x} for x in PERIOD_OPTIONS],
                        value='1y',
                        id="period_input",
                        inline=True,
                        className='textoTerciario',
                    ),
                ], sm=12, md=7),
                dbc.Col([
                    html.Span([
                            dbc.Label(className='fa fa-user-circle'),
                            dbc.Switch(id='profit_switch', value=True, className='d-inline-block ms-1'),
                            dbc.Label(className='fa fa-shopping-basket'),
                    ], className='textoTerciarioSwitchLineGraph'),
                ], sm=12, md=2, style={'text-align' : 'end'})
            ],  className='g-2 my-auto'),
        ], xs=12, md=12),     
    ],  className='g-2 my-auto'),
], fluid=True)

# Callback radar graph
@app.callback(
    Output('radar_graph', 'figure'),
    Input('book_data_store', 'data'),
    Input('radar_switch', 'value'),
)
def radar_graph(book_data, switch):
    df_registros = pd.DataFrame(book_data)
    df_registros['vol'] = abs(df_registros['vol']) * df_registros['tipo'].replace({'Compra': 1, 'Venda': -1})
    
    if switch:
        df_ibov_prop = df_ibov[df_ibov['Código'].isin(df_registros['ativo'].unique())]
        df_ibov_prop['Proporcao'] = df_ibov_prop['Participação'].apply(lambda x: x*100/df_ibov_prop['Participação'].sum())

        ibov_setor = df_ibov_prop.groupby('Setor')['Proporcao'].sum()

        df_registros = df_registros[df_registros['ativo'].isin(df_ibov['Código'].unique())]
        df_registros['Participação'] = df_registros['vol'].apply(lambda x: x*100/df_registros['vol'].sum())

        df_registros = df_registros.groupby('ativo')['Participação'].sum()
        df_registros = pd.DataFrame(df_registros).reset_index()

        try:
            df_registros['setores'] = np.concatenate([df_ibov_prop[df_ibov_prop['Código'] == ativo]['Setor'].values for ativo in df_registros['ativo']])
        except:
            df_registros['setores'] = 'Sem registros'
  
        df_registros = df_registros.groupby('setores')['Participação'].sum()

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=ibov_setor, theta=ibov_setor.index, name='IBOV', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_1)))
        fig.add_trace(go.Scatterpolar(r=df_registros, theta=df_registros.index, name='Carteira', fill='toself',
                                    hovertemplate ='<b>CARTEIRA</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_2)))
    else:
        df_total_ibov = df_ibov.groupby('Setor')['Participação'].sum() * 100
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=df_total_ibov, theta=df_total_ibov.index, name='Carteira', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_1)))

    fig.update_traces(line={'shape': 'spline'})
    fig.update_layout(MAIN_CONFIG, showlegend=True, height=TAMANHO_RADAR, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor = BACKGROUND_RADAR, angularaxis = dict(tickfont_size = TAMANHO_INDICADORES, color=INDICADORES, gridcolor=LINHA_Y, 
                    linecolor=LINHA_CIRCULAR_EXTERNA), radialaxis=dict(color=AXIS_X_VALUES_COLOR, gridcolor=LINHAS_CIRCULARES, linecolor=LINHA_X)))

    return fig

#callback para atualizar os cards
@app.callback(
    Output('ibov_valor', 'children'),
    Output('ibov_percent', 'children'),
    Output('carteira_valor', 'children'),
    Output('carteira_percent', 'children'),
    Output('cards_ativos', 'children'),
    State('historical_data_store', 'data'),
    Input('period_input', 'value'),
    Input('dropdown_card1', 'value'),
    Input('book_data_store', 'data'),
)

def update_cards_ativos(historical_data, period, dropdown, book_data):

    if dropdown == None:
        return no_update
    if type(dropdown) != list: dropdown = [dropdown]
    dropdown = ['IBOV'] + dropdown
    
    df_book = pd.DataFrame(book_data)
    df_hist = pd.DataFrame(historical_data)

    df_book['datetime'] = pd.to_datetime(df_book['date'], format='%Y-%m-%d %H:%M:%S')

    df2 = df_book.groupby(by=['ativo', 'tipo'])['vol'].sum()

    diferenca_ativos = {}
    # agrupa os dados por valores únicos na primeira coluna do índice (level = 0)
    for ativo, new_df in df2.groupby(level=0):
        compra, venda = 0, 0
        try:
            #salva os valores da linha dos ativos que tem 'compra'
            compra = new_df.xs((ativo, 'Compra'))
        except: pass
        try:
            #salva os valores da linha dos ativos que tem 'venda'
            venda = new_df.xs((ativo, 'Venda'))
        except: pass
        diferenca_ativos[ativo] = compra - venda

    #adiciona em um dicionario somente os ativos existentes na carteira
    ativos_existentes = dict((k, v) for k, v in diferenca_ativos.items() if v >= 0)
    ativos_existentes['IBOV'] = 1 #botei 1 pq era só pra adicionar um valor qualquer, o que importa é a chave 'IBOV'

    if period == 'ytd':
        correct_timedelta = date.today().replace(month=1, day=1)
        correct_timedelta = pd.Timestamp(correct_timedelta)
    else:
        correct_timedelta = date.today() - TIMEDELTAS[period]

    dict_valores = {}

    for key, value in ativos_existentes.items():
        df_auxiliar = (df_hist[df_hist.symbol.str.contains(key)])
        df_auxiliar['datetime'] = pd.to_datetime(df_auxiliar['datetime'], format='%Y-%m-%d %H:%M:%S')
        df_periodo = df_auxiliar[df_auxiliar['datetime'] > correct_timedelta]
        # import pdb; pdb.set_trace()
        valor_atual = df_periodo['close'].iloc[-1]
        diferenca_periodo= valor_atual/df_periodo['close'].iloc[0]
        dict_valores[key] = valor_atual, diferenca_periodo
        dfativos= pd.DataFrame(dict_valores).T.rename_axis('ticker').add_prefix('Value').reset_index()
        dfativos['Value1']= dfativos['Value1']*100 - 100
    
    seta_crescendo = ['fa fa-angle-up', 'textoQuartenarioVerde',]
    seta_caindo = ['fa fa-angle-down', 'textoQuartenarioVermelho']

    lista_valores_ativos = []
    lista_tags = []
    for ativo in range(len(dfativos)):
        tag_ativo = dfativos.iloc[ativo][0]
        lista_tags.append(tag_ativo)
        valor_ativo = dfativos.iloc[ativo][1]
        variacao_ativo = dfativos.iloc[ativo][2]
        if variacao_ativo < 0:
            lista_valores_ativos.append([tag_ativo, valor_ativo, variacao_ativo, seta_caindo[0], seta_caindo[1]])
        else: 
            lista_valores_ativos.append([tag_ativo, valor_ativo, variacao_ativo, seta_crescendo[0], seta_crescendo[1]])

    #Graficos
    df_hist = pd.DataFrame(historical_data)
    df_hist['datetime'] = pd.to_datetime(df_hist['datetime'], format='%Y-%m-%d %H:%M:%S')
    df_hist = slice_df_timedeltas(df_hist, period)

    df_hist = df_hist[df_hist['symbol'].str.contains('|'.join(lista_tags))]

    lista_graficos = []
    for n, ticker in enumerate(lista_tags):
        fig = go.Figure()
        df_aux = df_hist[df_hist.symbol.str.contains(ticker)]
        df_aux.dropna(inplace=True)
        df_aux.close = df_aux.close / df_aux.close.iloc[0] - 1

        fig.add_trace(go.Scatter(x=df_aux.datetime, y=df_aux.close*100, mode='lines', name=ticker,line=dict(color=CARD_GRAPHS_LINE_COLOR), hoverinfo = "skip"))

        fig.update_layout(MAIN_CONFIG_3, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        lista_graficos.append(fig)

    lista_colunas = []
    for n, ativo in enumerate(lista_valores_ativos):
        if ativo[0] != 'IBOV' and  n < 4:
            col = dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Legend(ativo[0], className='textoQuartenario'),
                                        
                                    ], md=4),
                                    dbc.Col([
                                        dcc.Graph(figure=lista_graficos[n], config={"displayModeBar": False, "showTips": False}, className='graph_cards'),
                                    ], md=8)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        html.H5(["R$",'{:,.2f}'.format(ativo[1]), " "], className='textoTerciario'),
                                        html.H5([html.I(className=ativo[3]), " ", '{:,.2f}'.format(ativo[2]), "%"], className=ativo[4])
                                    ])
                                ])
                            ])
                        ],className='cards_linha2'), 
                    ], md=3, xs=12)
            
            lista_colunas.append(col)

    card_ativos= dbc.Row([
                    *lista_colunas
                ])
    
    valor_ibov = html.Legend(["",'{:,.2f}'.format(dfativos['Value0'].iloc[-1]), " "], className='textoQuartenario'),

    ibov_percentual = dfativos['Value1'].iloc[-1]
    if ibov_percentual < 0:
        percent_ibov =  html.Legend([html.I(className=seta_caindo[0]), " ", '{:,.2f}'.format(ibov_percentual), "%"], className=seta_caindo[1])
    else:
         percent_ibov =  html.Legend([html.I(className=seta_crescendo[0]), " ", '{:,.2f}'.format(ibov_percentual), "%"], className=seta_crescendo[1])
    
    compra_e_venda = df_book.groupby('tipo')

    df_compra_e_venda = compra_e_venda.sum()
    if 'Venda' in compra_e_venda.groups and 'Compra' in compra_e_venda.groups:
        valor_carteira_original = df_compra_e_venda['valor_total']['Compra'] - df_compra_e_venda['valor_total']['Venda']
    elif  'Venda' in compra_e_venda.groups and 'Compra' not in compra_e_venda.groups:
        valor_carteira_original =  -df_compra_e_venda['valor_total']['Venda']  
    elif 'Venda' not in compra_e_venda.groups and 'Compra' in compra_e_venda.groups:
        valor_carteira_original = df_compra_e_venda['valor_total']['Compra']
    else:
        valor_carteira_original = "0.00"
   
    df_tipo_e_ativo = df_book.groupby(['tipo', 'ativo'])
    df_tipo_e_ativo_soma = df_tipo_e_ativo.sum()

    #verificando a quantidade de cada ativo que existe comprada na wallet
    lista_ativos = df_book['ativo'].unique()
    resultado = {}
    for ativo in lista_ativos:
        try:
            compra = df_tipo_e_ativo_soma['vol']['Compra'][ativo]
            venda = df_tipo_e_ativo_soma['vol']['Venda'][ativo]
            if compra > venda:
                qtd = compra - venda
                resultado[ativo] = qtd
        except:
            try:
                qtd = df_tipo_e_ativo_soma['vol']['Compra'][ativo]
                resultado[ativo] = qtd
            except:
                pass
    
    valor_total = 0
    for ativo, qtd in resultado.items():
        for id, ativos in enumerate(lista_valores_ativos):
            if ativo == ativos[0]:
                total = qtd * ativos[1]
                valor_total += total

    if valor_carteira_original == "0.00":
        valor_carteira_original = 0
        varicao_carteira = 0
        varicao_carteira_configurado = 0
    else:
        varicao_carteira = valor_total/float(valor_carteira_original)
        varicao_carteira_configurado = valor_total/float(valor_carteira_original)*100 - 100

    valor_carteira_atual =  html.Legend("R$" + '{:,.2f}'.format(valor_carteira_original*varicao_carteira), className='textoSecundario')

    if varicao_carteira < 1:
        percentual_carteira =  html.Legend([html.I(className=seta_caindo[0]), " ", '{:,.2f}'.format(varicao_carteira_configurado), "%"], className=seta_caindo[1])
    else:
         percentual_carteira =  html.Legend([html.I(className=seta_crescendo[0]), " ", '{:,.2f}'.format(varicao_carteira_configurado), "%"], className=seta_crescendo[1])

    return valor_ibov, percent_ibov, valor_carteira_atual, percentual_carteira, card_ativos