import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import export_graphviz
import graphviz

# Carregando o conjunto de dados de um arquivo de texto
with open('data_base.txt', 'r') as file:
    lines = file.readlines()

# Convertendo os dados em uma lista de listas
data = [line.strip().split(',') for line in lines]

# Convertendo a lista de listas em um DataFrame do pandas
df = pd.DataFrame(data)

# Dividindo os dados em atributos (X) e rótulos (y)
X = df.drop(df.columns[-1], axis=1)  # assumindo que a última coluna contém os rótulos
y = df[df.columns[-1]]

# Dividindo os dados em conjunto de treinamento e conjunto de teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Criando o classificador de árvore de decisão
classifier = DecisionTreeClassifier()

# Treinando o classificador
classifier.fit(X_train, y_train)

# Fazendo previsões no conjunto de teste
y_pred = classifier.predict(X_test)

# Avaliando a precisão do modelo
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Exportando a árvore de decisão para um arquivo .dot
export_graphviz(classifier, out_file='tree.dot', 
                feature_names=X.columns,
                class_names=y.unique(),
                rounded=True, filled=True)

# Convertendo o arquivo .dot para um formato de imagem
with open('tree.dot') as f:
    dot_graph = f.read()
graph = graphviz.Source(dot_graph)
graph.render(filename='decision_tree', format='png', cleanup=True)

# Visualizando a árvore de decisão
graph
