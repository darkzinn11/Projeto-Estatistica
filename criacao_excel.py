import pandas as pd
import numpy as np
import random

# Criando um DataFrame com dados fictícios
df = pd.DataFrame({
    'Data': pd.date_range(start='1/1/2023', periods=100),
    'Vendas': np.random.randint(100, 1000, size=100),
    'Despesas': np.random.randint(50, 500, size=100),
    'Satisfacao': np.random.randint(1, 10, size=100)
})

# Lista de categorias de produtos expandida
categorias_expandidas = [
    'Eletrônicos', 'Roupas', 'Alimentos', 'Livros', 'Móveis', 'Jogos', 'Esportes', 'Jardinagem',
    'Bebidas', 'Frutas', 'Legumes', 'Carnes', 'Peixes', 'Laticínios', 'Padaria', 'Congelados',
    'Doces', 'Snacks', 'Cereais', 'Condimentos', 'Especiarias', 'Grãos', 'Massas', 'Sopas',
    'Conservas', 'Biscoitos', 'Sorvetes', 'Café', 'Chás', 'Sucos', 'Águas', 'Refrigerantes',
    'Artigos de Festa', 'Utensílios de Cozinha', 'Limpeza', 'Higiene Pessoal', 'Perfumaria',
    'Maquiagem', 'Farmácia', 'Pet Shop', 'Brinquedos', 'Papelaria', 'Eletrodomésticos',
    'Informática', 'Celulares', 'Fotografia', 'Decoração', 'Cama, Mesa e Banho', 'Ferramentas',
    'Automotivos', 'Construção', 'Jardinagem Avançada'
]

# Atualizando a coluna 'Produtos' com a nova lista de categorias
df['Produtos'] = [random.choice(categorias_expandidas) for _ in range(len(df))]

# Salvando o DataFrame atualizado como um arquivo Excel
df.to_excel('dados_empresa.xlsx', index=False)
