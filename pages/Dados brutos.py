import streamlit as st
import requests
import pandas as pd
import time

# Função para converter DataFrame em CSV e fazer cache do resultado
@st.cache_data
def convert_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para exibir mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

# Título da aplicação
st.title('DADOS BRUTOS')

# Carregar dados da URL
url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

# Seleção de colunas
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Filtros no sidebar
st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Local da compra'):
    local_da_compra = st.multiselect('Selecione o local', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

# Aplicar filtros nos dados
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Local da compra` in @local_da_compra and \
`Tipo de pagamento` in @tipo_pagamento
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Exibir dados filtrados
st.dataframe(dados_filtrados)

# Exibir contagem de linhas e colunas
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

# Input para nome do arquivo e botão de download
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button(
        'Fazer o download da tabela em csv', 
        data=convert_csv(dados_filtrados),
        file_name=nome_arquivo, 
        mime='text/csv', 
        on_click=mensagem_sucesso
    )
