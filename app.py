from flask import Flask, render_template, request
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    # Verifique se o post request tem o arquivo parte
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # Se o usuário não selecionar o arquivo, o navegador também
    # enviar um arquivo vazio sem nome.
    if file.filename == '':
        return 'No selected file'
    if file:
        df = pd.read_excel(file)
        
        # Mapeamento dinâmico de colunas
        column_mapping = {
            'Data': None,
            'Vendas': None,
            'Despesas': None,
            'Satisfacao': None,
            'Produtos': None
        }

        # Tente encontrar colunas correspondentes ou semelhantes
        for col in df.columns:
            for key in column_mapping.keys():
                if key.lower() in col.lower():
                    column_mapping[key] = col

        # Verifique se todas as colunas necessárias foram encontradas
        if None in column_mapping.values():
            missing_columns = [key for key, value in column_mapping.items() if value is None]
            return f'Excel file is missing the following columns: {missing_columns}'

        # Atualize o DataFrame para usar os nomes de colunas mapeados
        df.rename(columns=column_mapping, inplace=True)

        # Processamento dos dados conforme necessário
        # Definindo as faixas de cores
        bins = [0, df['Despesas'].max() / 3, 2 * df['Despesas'].max() / 3, df['Despesas'].max()]
        labels = ['green', 'yellow', 'red']
        df['color'] = pd.cut(df['Despesas'], bins=bins, labels=labels)

        # Calculando estatísticas descritivas para cada categoria de produto
        media_vendas_por_produto = df.groupby('Produtos')['Vendas'].mean().round(2).reset_index()
        media_despesas_por_produto = df.groupby('Produtos')['Despesas'].mean().round(2).reset_index()
        media_satisfacao_por_produto = df.groupby('Produtos')['Satisfacao'].mean().round(2).reset_index()

        # Criando subplots
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, specs=[[{"type": "scatter"}], [{}], [{}], [{"type": "table"}]], row_heights=[0.7, 0.07, 0.07, 0.25])

        # Perguntando ao usuário qual visualização ele gostaria de ver
        opcao = request.form.get('opcao')

        # Removendo os traços existentes
        fig.data = []

        # Adicionando visualizações baseadas na opção escolhida
        if opcao == '1':
            # Criando um gráfico de linha para 'Vendas e Receitas'
            fig.add_trace(go.Scatter(x=df['Data'], y=df['Vendas'], mode='lines+markers', marker=dict(color='royalblue', size=10, line=dict(color='DarkSlateGrey', width=2))), row=1, col=1)
            fig.update_layout(title='Vendas e Receitas ao Longo do Tempo', title_x=0.5, plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='lightgray')

            # Adicionando a tabela de média de vendas no quarto subplot
            fig.add_trace(
                go.Table(
                    header=dict(values=['Produtos', 'Data', 'Vendas', 'Despesas', 'Satisfacao', 'Média de Vendas por Produto'], fill_color='paleturquoise', align='left'),
                    cells=dict(values=[df.Produtos, df.Data, df.Vendas, df.Despesas, df.Satisfacao, [media_vendas_por_produto.loc[media_vendas_por_produto['Produtos'] == produto, 'Vendas'].values[0] if produto in media_vendas_por_produto['Produtos'].values else None for produto in df['Produtos']]], fill_color='lavender', align='left')),
                row=4, col=1
            )

        elif opcao == '2':
            # Criando um gráfico de barras para 'Despesas'
            fig.add_trace(go.Bar(x=df['Data'], y=df['Despesas'], marker_color=df['color']), row=1, col=1)
            fig.update_layout(title='Despesas ao Longo do Tempo', title_x=0.5, plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='lightgray')

            # Adicionando a tabela de média de despesas no quarto subplot
            fig.add_trace(
                go.Table(
                    header=dict(values=['Produtos', 'Data', 'Vendas', 'Despesas', 'Satisfacao', 'Média de Despesas por Produto'], fill_color='paleturquoise', align='left'),
                    cells=dict(values=[df.Produtos, df.Data, df.Vendas, df.Despesas, df.Satisfacao, [media_despesas_por_produto.loc[media_despesas_por_produto['Produtos'] == produto, 'Despesas'].values[0] if produto in media_despesas_por_produto['Produtos'].values else None for produto in df['Produtos']]], fill_color='lavender', align='left')),
                row=4, col=1
            )

        elif opcao == '3':
            # Criando um gráfico de linha para 'Satisfação do Cliente'
            fig.add_trace(go.Scatter(x=df['Data'], y=df['Satisfacao'], mode='lines+markers', marker=dict(color='firebrick', size=10, line=dict(color='DarkSlateGrey', width=2))), row=1, col=1)
            fig.update_layout(title='Satisfação do Cliente ao Longo do Tempo', title_x=0.5, plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='lightgray')

            # Adicionando a tabela de média de satisfação no quarto subplot
            fig.add_trace(
                go.Table(
                    header=dict(values=['Produtos', 'Data', 'Vendas', 'Despesas', 'Satisfacao', 'Média de Satisfação por Produto'], fill_color='paleturquoise', align='left'),
                    cells=dict(values=[df.Produtos, df.Data, df.Vendas, df.Despesas, df.Satisfacao, [media_satisfacao_por_produto.loc[media_satisfacao_por_produto['Produtos'] == produto, 'Satisfacao'].values[0] if produto in media_satisfacao_por_produto['Produtos'].values else None for produto in df['Produtos']]], fill_color='lavender', align='left')),
                row=4, col=1
            )

        else:
            return "Opção inválida. Por favor, escolha 1, 2, 3 ou 4."

        # Adicionando o Range Slider e o Selector
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            height=1000  # Ajustar a altura  
        )

        # Converta seus gráficos Plotly em JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

if __name__ == '__main__':
    app.run(debug=True)
