import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /=1000
    return f'{prefixo} {valor:.2f} {unidade} milhões'


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil','Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

#barra lateral
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(),'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

##Tabelas 
###tabelas de receita
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on= 'Local da compra', right_index= True).sort_values('Preço', ascending= False)
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)
###tabelas de quantidade de vendas
qtd_vendas = dados.groupby('Local da compra')[['Preço']].sum()
local_compra_unique = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(qtd_vendas,left_on='Local da compra', right_index= True).sort_values('Preço', ascending=False)
qtd_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()
qtd_vendas_categoria = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending=False))
###tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

##Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat= 'lat',
                                  lon= 'lon',
                                  scope='south america',
                                  size= 'Preço',
                                  template= 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title= 'Receita por estado'
                                  )

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y= (0, receita_mensal.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(), 
                             x= 'Local da compra',
                             y= 'Preço',
                             text_auto= True,
                             title= 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')
fig_qtd_vendas = px.scatter_geo(local_compra_unique,
                                  lat= 'lat',
                                  lon= 'lon',
                                  scope='south america',
                                  size= 'Preço',
                                  template= 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title= 'Quantidade de venda por estado'
                                  )
fig_vendas_mensal = px.line(qtd_vendas_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y= (0, receita_mensal.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Vendas mensal')
fig_vendas_categoria = px.bar(qtd_vendas_categoria,
                              text_auto=True,
                              title='Vendas por categoria')
fig_vendas_categoria.update_layout(showlegend = False, yaxis_title = 'Quantidade de vendas')

## Visuablização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

#aba1

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)

#aba 2

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
    st.plotly_chart(fig_qtd_vendas)
    st.plotly_chart(fig_vendas_mensal)
    st.plotly_chart(fig_vendas_categoria, use_container_width= True)


#aba 3

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores),
                                        x = vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores).index,
                                        y= 'sum',
                                        text_auto= True,
                                        title=f'Top {qtd_vendedores} vendedores(receita)')
        st.plotly_chart(fig_receita_vendedores)                   
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores),
                                        x = vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores).index,
                                        y= 'count',
                                        text_auto= True,
                                        title=f'Top {qtd_vendedores} vendedores(quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)

st.dataframe(dados)

