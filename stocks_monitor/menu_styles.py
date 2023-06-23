COR_LEGENDA = 'rgba(255,255,255,0.4)'

#menu radar graph
INDICADORES = 'rgba(255,255,255,0.4)'
BACKGROUND_RADAR = 'rgba(178, 45, 178, 1)'  
LINHA_X = 'white'
LINHA_Y = 'white'
LINHAS_CIRCULARES = '#0d0834'
LINHA_CIRCULAR_EXTERNA = '#0d0834'
LINHAS_PREENCHIMENTO_1 = 'white'
LINHAS_PREENCHIMENTO_2 = '#0d0834'
CAIXA_LEGENDA = 'rgba(255,255,255,0.1)'
AXIS_X_VALUES_COLOR = 'rgba(0,0,0,0)'
TAMANHO_INDICADORES = 15
TAMANHO_RADAR = 190

#menu line graph
AXIS_FONT_SIZE = 20
AXIS_VALUES_COLOR = 'white'
LINHAS_DE_GRADE = 'rgba(255,255,255,0.1)'
LINHA_ZERO_X = 'rgba(255,255,255,0.2)'
LINHA_EVOLUCAO_PATRIMONIAL = 'rgba(178, 45, 178, 1)' 
LISTA_DE_CORES_LINHAS = ['rgba(178, 45, 178, 1)', 'rgba(76,0,176,0.4)', 'rgba(138,0,176,0.4)', 'rgba(103,0,103,0.4)', 'rgba(87,53,106,0.4)', 'rgba(177,0,205,0.4)', 'rgba(190,46,214,0.4)', 'white']
HOVER_LINE_GRAPH = {
        "bgcolor":"rgba(32, 36, 73, 0.7)",
        "font" : {'color':COR_LEGENDA}
}
#PREENCHIMENTO_LINE_GRAPH = 'rgba(178, 45, 178, 0.1)'

#cards fixed_row
CARD_GRAPHS_LINE_COLOR = 'rgba(178, 45, 178, 0.5)'

#radar graph
MAIN_CONFIG = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":1.0, 
                "xanchor":"left",
                "x":1.0,
                "title": {"text": None},
                "bgcolor": CAIXA_LEGENDA},
    "font" : {'color': COR_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}

#line graph
MAIN_CONFIG_2 = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.25, 
                "xanchor":"left",
                "x":0.05,
                "bgcolor": CAIXA_LEGENDA},
    "font" : {'color': COR_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}

#cards graph
MAIN_CONFIG_3 = {
    # "hovermode": "x unified",
    "legend": {"bgcolor": 'rgba(0,0,0,0)'},
    "font" : None,
    "margin": {"l":0, "r":0, "t":0, "b":0},
}


HEIGHT={'height': '100%'}