from dash import dcc
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd

from components import home, header, wallet, fixed_row
from functions import *
from app import *


# Funções =======================================
# Checando se o book de transações existe
ativos_org = {}
try:    # caso exista, ler infos
    df_book = pd.read_csv('book_data.csv', index_col=0)
    ativos_org = iterar_sobre_df_book(df_book)
except: # caso não exista, criar df
    df_book = pd.DataFrame(columns=['date', 'preco', 'tipo', 'ativo', 'exchange', 'vol', 'valor_total'])

try:
    df_historical_data = pd.read_csv('historical_data.csv', index_col=0)
except:
    df_historical_data = pd.DataFrame(columns=['datetime', 'symbol', 'close'])

df_historical_data = atualizar_historical_data(df_historical_data, ativos_org)

df_book = df_book.to_dict() 
df_historical_data = df_historical_data.to_dict()

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dcc.Store(id='book_data_store', data=df_book, storage_type='memory'),
    dcc.Store(id='historical_data_store', data=df_historical_data, storage_type='memory'),
    dcc.Store(id='layout_data', data=[], storage_type='memory'),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    header.layout
                ], className= 'header_layout'),
            ]),
            dbc.Row([
                dbc.Col([
                   fixed_row.layout
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                ]),
            ],id="page-content"),
        ])
    ])
], fluid=True)

# Callbacks =======================
#atualiza o content da pagina quando clica em algum dos icones do header
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)

def render_page(pathname):
    if pathname == '/home' or pathname == '/':
        return home.layout
    if pathname == '/wallet':
        return wallet.layout

#Callback para atualizar as databases
@app.callback(
    Output('historical_data_store', 'data'),
    Input('book_data_store', 'data'),
    State('historical_data_store', 'data')
)
def atualizar_databases(book_data, historical_data):
    df_book = pd.DataFrame(book_data)
    df_historical = pd.DataFrame(historical_data)

    ativos = iterar_sobre_df_book(df_book)

    df_historical = atualizar_historical_data(df_historical, ativos)

    df_historical.to_csv('historical_data.csv')

    return df_historical.to_dict()


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)