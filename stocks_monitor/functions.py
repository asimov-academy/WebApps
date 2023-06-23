import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from datetime import date
from tvdatafeed_lib.main import TvDatafeed

#offsets são deltas entre a data atual e o valor inserido no parametro
offsets = [DateOffset(days=5), DateOffset(months=1), DateOffset(months=3), DateOffset(months=6), DateOffset(years=1), DateOffset(years=2)] 
delta_titles = ['5 dias', '1 mês', '3 meses', '6 meses', '1 ano', '2 anos', 'Ano até agora']
PERIOD_OPTIONS = ['5d','1mo','3mo','6mo','1y','2y', 'ytd']

#itera sobre as tuplas de periodo opetion e offsets
TIMEDELTAS = {x: y for x, y in zip(PERIOD_OPTIONS, offsets)}
TITLES = {x: y for x, y in zip(PERIOD_OPTIONS, delta_titles)}

#esse trecho abaixo é utilizado na atualização do radar graph
df_ibov = pd.read_csv('tabela_ibov.csv')

#trata os valores de cada coluna do df_ibov
df_ibov['Part. (%)'] = pd.to_numeric(df_ibov['Part. (%)'].str.replace(',','.'))
df_ibov['Qtde. Teórica'] = pd.to_numeric(df_ibov['Qtde. Teórica'].str.replace('.', ''))
df_ibov['Participação'] = df_ibov['Qtde. Teórica'] / df_ibov['Qtde. Teórica'].sum()
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: x.split('/')[0].rstrip())
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: 'Cons N Cíclico' if x == 'Cons N Ciclico' else x)

def definir_evolucao_patrimonial(df_historical_data: pd.DataFrame, df_book_data: pd.DataFrame) -> pd.DataFrame:

    #altera os indices do dataframe para as datas de cada linha
    df_historical_data = df_historical_data.set_index('datetime')
    #adiciona uma nova coluna chamada date, que pega a data que está no index e a transforma para dados do tipo date (geralmente vem como timestamp, datetime,
    # string etc.)
    df_historical_data['date'] = df_historical_data.index.date
    # agrupa o df pelas duas colunas "date" e "symbol" e, em seguida, pega o último valor da coluna "close" para cada grupo formado pelas duas colunas do 
    # agrupamento. O método "to_frame()" converte a série resultante em um DataFrame e o método "reset_index()" redefine os índices do DataFrame para começar em zero
    df_historical_data = df_historical_data.groupby(['date', 'symbol'])['close'].last().to_frame().reset_index()
    #faz um pivot table para agrupar o dataframe em colunas de acordo com o 'symbol' de cada uma delas, que é basicamente agrupar as colunas por cada ativo,
    #utilizando como dados os valores de 'cole' e o index como 'date'
    df_historical_data = df_historical_data.pivot(values='close', columns='symbol', index='date')

    #cria dois dataframes auxiliares iguais ao dataframe da etapa anterior
    df_cotacoes = df_historical_data.copy()
    df_carteira = df_historical_data.copy()

    # substitui todos os 0s no DataFrame por valores NaN reenche para frente os valores ausentes com o último valor conhecido em cada coluna. 
    # Ou seja, substitui cada valor NaN com o valor mais recente e não nulo na mesma coluna. E por fim O método .fillna(0) substitui quaisquer
    # valores NaN restantes por 0.
    df_cotacoes = df_cotacoes.replace({0: np.nan}).ffill().fillna(0)
    # remove a string 'BMFBOVESPA' do titulo de cada linha dos dataframes cotacoes e carteira (splitando nos : que onde está a string)
    df_cotacoes.columns = [col.split(':')[-1] for col in df_cotacoes.columns]
    df_carteira.columns = [col.split(':')[-1] for col in df_carteira.columns]
    
    #deleta a coluna 'IBOV' dos dois dataframes 
    del df_carteira['IBOV'], df_cotacoes['IBOV']
    # faz um replace dos valores de compra e venda, na coluna 'tipo', quando for compra é 1 e quando for venda é -1 e depois multiplica os valores
    #da coluna 'vol' para que as quantidades fiquem com o sinal do tipo da operação, quantidade negativa quando for venda e quantidade positiva quando for compra
    df_book_data['vol'] = df_book_data['vol'] * df_book_data['tipo'].replace({'Compra': 1, 'Venda': -1})
    #altera o tipo dos valores da coluna data para datetime
    df_book_data['date'] = pd.to_datetime(df_book_data.date)
    #transforma o index do df nas datas
    df_book_data.index = df_book_data['date'] 
    #torna os valores da coluna 'date' iguais aos valores do index, para garantir que os dados sejam do mesmo tipo
    df_book_data['date'] = df_book_data.index.date
    
    #seleciona todas as linhas e colunas do df_carteira e transforma tudo em zero, todas as células do df se tornam zero
    df_carteira.iloc[:, :] = 0

    #itera por todas as linhas do df_book_data e, para todas as céululas que possuirem valores maior que os valores da mesma céula no df_carteira, no caso maior que zero
    # vai ser colocada a quantidade real de cada ativo que o usuario possui (compra - venda) nas respectivas datas
    for _, row in df_book_data.iterrows():
        df_carteira.loc[df_carteira.index >= row['date'], row['ativo']] += row['vol']
    
    #cria um novo df em que vai conter o valor total de cada ativo que o usuario possui, multiplicando as quantidade pelos respectivos preços de cada ativo
    df_patrimonio = df_cotacoes * df_carteira
    #substitui todos os valores NaN (valores nao encontrados, dados ausentes, por zero)
    df_patrimonio = df_patrimonio.fillna(0)
    #cria uma nova coluna no df_patrimonio chamada 'soma, que vai conter justamente a soma do valor de todos os ativos em cada data, resultado no valor total em dinheiro 
    #que o usuario tem em ativos por data
    df_patrimonio['soma'] = df_patrimonio.sum(axis=1)
    # cria um novo DataFrame que contém a quantidade de ações que cada ativo tem na carteira
    df_ops = df_carteira - df_carteira.shift(1)
    #multiplica os valores pelos valores das cotações atuais de cada ativo
    #basicamente nesse dataframe vamos ter o valor atualizada de cada ação, de acordo com o preço atual de cada ativo baseado na quantidade que existe comprada na
    #carteira do usuario
    df_ops = df_ops * df_cotacoes
    
    #cria uma nova coluna chamada evolucao patrimonial no df onde vamos pegar as diferenças dos valores da coluna soma entre datas adjacentes e diminuir dos valores
    #do df que contem as os valores de todas as açoes da carteira
    df_patrimonio['evolucao_patrimonial'] = df_patrimonio['soma'].diff() - df_ops.sum(axis=1)           # .plot()
    # e aqui realizamos a divisão para ver o percentual, armazenando esse valor em uma nova coluna chamada evolucao percentual
    df_patrimonio['evolucao_percentual'] = (df_patrimonio['evolucao_patrimonial'] / df_patrimonio['soma'])

    # cria uma lista chamada ev_total_list com o mesmo comprimento do DataFrame df_patrimonio e preenche todos os elementos da lista com o valor 1. vamos usar
    # esses valores de 1 justamente para incrementar ou decrementar o percentual da variacao de cada açao
    ev_total_list = [1]*len(df_patrimonio)
    df_patrimonio['evolucao_percentual'] = df_patrimonio['evolucao_percentual'].fillna(0)
    
    # calcula uma nova coluna "evolucao_cum" que armazena o valor acumulado da evolução percentual.
    for i, x in enumerate(df_patrimonio['evolucao_percentual'].to_list()[1:]):
        ev_total_list[i+1] = ev_total_list[i] * (1 + x)
        df_patrimonio['evolucao_cum'] = ev_total_list
    
    return df_patrimonio

def slice_df_timedeltas(df: pd.DataFrame, period_string: str) -> pd.DataFrame:
    if period_string == 'ytd':
        correct_timedelta = date.today().replace(month=1, day=1)
        correct_timedelta = pd.Timestamp(correct_timedelta)
    else:
        correct_timedelta = date.today() - TIMEDELTAS[period_string]
    df = df[df.datetime > correct_timedelta].sort_values('datetime')
    return df

try:
    df_book_data = pd.read_csv('book_data.csv', index_col=0)
    df_compra_e_venda = df_book_data.groupby('tipo').sum()
except:
    df_book = pd.DataFrame(columns=['date', 'preco', 'tipo', 'ativo', 'exchange', 'vol', 'valor_total'])

def iterar_sobre_df_book(df_book_var: pd.DataFrame, ativos_org_var={}) -> dict:
    for _, row in df_book_var.iterrows():
        if not any(row['ativo'] in sublist for sublist in ativos_org_var):  
            ativos_org_var[row["ativo"]] = row['exchange']
    
    ativos_org_var['IBOV'] = 'BMFBOVESPA'
    return ativos_org_var 

def atualizar_historical_data(df_historical_var: pd.DataFrame, ativos_org_var={}) -> pd.DataFrame:
    tv = TvDatafeed()
    for symb_dict in ativos_org_var.items():
        new_line = tv.get_hist(*symb_dict, n_bars=5000)[['symbol','close']].reset_index()

        df_historical_var = pd.concat([df_historical_var, new_line], ignore_index=True)

    return df_historical_var.drop_duplicates(ignore_index=True)
