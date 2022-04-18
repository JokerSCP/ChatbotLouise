from APIManager import APIManager
from ProcessingTextManager import ProcessingTextManager
import json
import random
import pickle
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

# Coletando dados e bag de intentions
api_manager = APIManager(True)
api_manager.get_token()
api_manager.get_apikey()
intention_bag = api_manager.get_chatbot_intention_bag_list()

# Criando processador de texto
text_manager = ProcessingTextManager(True)

# Salvando arquivo json
file = open('../Models/intentionBag.json', 'w')
file.write(json.dumps(intention_bag))
file.close()

# Variáveis
words = []
classes = []
documents = []

# Monta a estrutura da bag of words
for intent in intention_bag:
    for bow in intent['bagOfWordList']:
        word_list = text_manager.process_sentence(bow)
        words.extend(word_list)
        documents.append((word_list, intent['classIntention']))
        if intent['classIntention'] not in classes:
            classes.append(intent['classIntention'])

# Ordena as matrizes, exibe o resultado
words = sorted(set(words))
classes = sorted(set(classes))
print("Words: {}".format(words))

# Salva arquivos do modelo
pickle.dump(words, open('../Models/words.pkl', 'wb'))
pickle.dump(classes, open('../Models/classes.pkl', 'wb'))

# Contagem da BOW e montagem das variáveis da rede neural
training = []
output_empty = [0] * len(classes)
for document in documents:
    bag = []
    patterns = document[0]
    for word in words:
        bag.append(1) if word in patterns else bag.append(0)
    print(bag)
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

# Variaveis para treinamento
random.shuffle(training)
training = np.array(training)
train_x = list(training[:, 0])
train_y = list(training[:, 1])
# print(training)

# Rede neural
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]), ), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(116, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Parâmetros de aprendizado e salvamento do modelo
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
history = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('../Models/louise.model', history)

print("Modelo processado!")
