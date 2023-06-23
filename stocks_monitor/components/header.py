from dash import html
import dash_bootstrap_components as dbc

from components import modal

layout = dbc.Container([
    dbc.Row([
    modal.layout,
        dbc.Col([
            dbc.Button("Home", href='/home', className='header_icon')
        ], md=1,xs=4), 
        dbc.Col([
            dbc.Button("Wallet", href='/wallet', className='header_icon')
        ], md=1,xs=4),
        dbc.Col([
            dbc.Button("Add", href='', id='add_button', className='header_icon')
        ], md=1,xs=4),
        html.Hr(style={'color' : 'rgba(255, 255, 255, 0.6)'})
    ], className='g-2 my-auto'),

], fluid=True)