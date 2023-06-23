from dash import html, callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import json
from tvdatafeed_lib.main import TvDatafeed

from components.modal import *
from app import *

tv = TvDatafeed()

card_sem_registros = dbc.Card([
                        dbc.CardBody([
                            html.Legend("Nenhum registro efetuado", className='textoQuartenarioBranco')
                        ])
                    ], className='card_sem_registros')


def generate_card(info_do_ativo):
    new_card =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-list-alt', style={"fontSize": '85%'}), " Nome: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['ativo']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),                              
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-database', style={"fontSize": '85%'}), " Quantidade: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['vol']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-money', style={"fontSize": '85%'}), " Unitário: "], className='textoQuartenario'),
                                        html.H5('{:,.2f}'.format(info_do_ativo['preco']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-calendar', style={"fontSize": '85%'}), " Data: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['date'])[:10], className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-handshake-o', style={"fontSize": '85%'}), " Tipo: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['tipo']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-money', style={"fontSize": '85%'}), " Total: "], className='textoQuartenario'),
                                        html.H5('{:,.2f}'.format(info_do_ativo['preco']*info_do_ativo['vol']), className='textoQuartenarioBranco'),
                                    ], md=2, style={'text-align' : 'left'}),
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                            dbc.Col([
                                dbc.Button([html.I(className = "fa fa-trash header-icon", 
                                                    style={'font-size' : '150%'})],
                                                    id={'type': 'delete_event', 'index': info_do_ativo['id']},
                                                    style={'background-color' : 'transparent', 'border-color' : 'transparent', 'padding' : '0px'}
                                                ), 
                            ], md=1, xs=12, style={'text-align' : 'right'})
                        ])
                    ])
                ], class_name=info_do_ativo['class_card'])
            ])
        ], className='g-2 my-auto')

    return new_card

def generate_list_of_cards(df):
    lista_de_dicts = []
    for row in df.index:
        infos = df.loc[row].to_dict()
        #altera nome da classe do card se for compra ou venda
        if infos['tipo'] == 'Compra':
            infos['class_card'] = 'card_compra'
        else:
            infos['class_card'] = 'card_venda'
        infos['id'] = row
        lista_de_dicts.append(infos)

    lista_de_cards = []
    for dicio in lista_de_dicts:
        card = generate_card(dicio)
        lista_de_cards.append(card)
    return lista_de_cards

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
    
        ], md=12, id='layout_wallet', style={"height": "100%", "maxHeight": "36rem", "overflow-y": "auto"})
    ], className='g-2 my-auto')
],fluid=True),

# Callbacks =======================
#call back auxiliar para ativar o layout da wallet
@app.callback(
    Output('layout_wallet', 'children'),
    Input('layout_data', 'data')
)
def func_auxiliar(data):
    return data

#callback que realiza alterações nos ativos da wallet
@app.callback(
    Output('modal', 'is_open'),
    Output('book_data_store', 'data'),
    Output ('layout_data', 'data'),

    Input('add_button', 'n_clicks'),
    Input('submit_cadastro', 'n_clicks'),
    Input('book_data_store', 'data'),
    Input({'type': 'delete_event', 'index': ALL}, 'n_clicks'),

    State('nome_ativo', 'value'),
    State('modal', 'is_open'),
    State('compra_venda_radio', 'value'),
    State('preco_ativo', 'value'),
    State('data_ativo', 'date'),
    State('quantidade_ativo', 'value'), 
)
def func_modal(n1, n2, book_data, event, ativo, open, radio, preco, periodo, vol):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    df_book_data = pd.DataFrame(book_data)
    df_book_data = df_book_data.sort_values(by='date', ascending=True)

    lista_de_cards = generate_list_of_cards(df_book_data)
    #verifica se nao tem nenhum ativo na lista de cards, caso nao tiver nada retorna o card com a msg 'nenhum registro efetuado'
    if len(lista_de_cards) == 0:
        lista_de_cards = card_sem_registros
    if trigg_id == '':
        df_book_data = df_book_data.sort_values(by='date', ascending=True)
        return [open, book_data, lista_de_cards]

    # 1. Botão de abrir modal
    if trigg_id == 'add_button':
        return [not open, book_data, lista_de_cards]
    
    # 2. Salvando ativo
    elif trigg_id == 'submit_cadastro':  # Corrigir caso de erro - None
        if None in [ativo, preco, vol] and open:
            return [open, book_data, lista_de_cards]
        else:
            ativo = ativo.upper()
            if tv.search_symbol(ativo,'BMFBOVESPA'):
                exchange = 'BMFBOVESPA'
                preco = round(preco, 2)
                df_book_data.loc[len(df_book_data)] = [periodo, preco, radio, ativo, exchange ,vol, vol*preco]    
                df_book_data['date'] = pd.to_datetime(df_book_data['date'], format='%Y-%m-%d')
                df_book_data.reset_index(drop=True, inplace=True)
                df_book_data = df_book_data.sort_values(by='date', ascending=True)

                df_book_data.to_csv('book_data.csv')
                book_data = df_book_data.to_dict()
                
                lista_de_cards = generate_list_of_cards(df_book_data)

                return [not open, book_data, lista_de_cards]

            else:   
                return [not open, book_data, lista_de_cards]

    # 3. Caso de delete de card
    if 'delete_event' in trigg_id:
        trigg_dict = callback_context.triggered[0]

        #verifica se nao foi clicado na atualização inicial do callback para nao deletar nenhum card
        if trigg_dict['value'] == None:
            return [open, book_data, lista_de_cards]

        trigg_id = json.loads(trigg_id)
        df_book_data.drop([str(trigg_id['index'])], inplace=True)
        df_book_data.reset_index(drop=True, inplace=True)
        df_book_data = df_book_data.sort_values(by='date', ascending=True)
        df_book_data.to_csv('book_data.csv')
        book_data = df_book_data.to_dict()
        lista_de_cards = generate_list_of_cards(df_book_data)

        if len(lista_de_cards) == 0:
            lista_de_cards = card_sem_registros

        return [open, book_data, lista_de_cards]

    return [open, book_data, lista_de_cards]