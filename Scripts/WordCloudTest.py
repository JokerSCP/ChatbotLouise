import matplotlib.pyplot as plt
from wordcloud import WordCloud
from APIManager import APIManager
from ProcessingTextManager import ProcessingTextManager


# Funcao local
def matrix_to_text(matrix):
    aux = ""
    especific_stopwords = ["start", "sim", "nao", "não", "fim", "oi", "fazer", "querer", "saber"]
    for word in matrix:
        if word not in especific_stopwords:
            aux = aux + " " + word
    return aux


# Iniciando managers
api_manager = APIManager(False)
text_manager = ProcessingTextManager(False, False, False)
text_manager_lem = ProcessingTextManager(False, True, True)

# Coleta dados da API e transforma em texto único
api_text_list = api_manager.get_message_list()
api_text = []
for message in api_text_list:
    if message.get("messageText") is not None:
        api_text.append(message.get("messageText"))
print("Valores em matriz: {}".format(api_text))

# Transformação sem lemmatization
text_aux = matrix_to_text(api_text)
text_list = text_manager.process_sentence(text_aux)
text = matrix_to_text(text_list)

# Transformação com lemmatization
text_aux_lem = matrix_to_text(api_text)
text_list_lem = text_manager_lem.process_sentence(text_aux_lem)
text_lem = matrix_to_text(text_list_lem)

# Nuvem de palavras
wc = WordCloud(width=760, height=540, collocations=False, background_color="white", mode="RGB")
wc.generate(text)
plt.figure(figsize=(16, 9))
plt.axis("off")
plt.imshow(wc, interpolation="bilinear")
plt.savefig('../Models/wordcloud.png', transparent=True)
plt.show()

# Nuvem de palavras com lemmatization
wc_lem = WordCloud(width=760, height=540, collocations=False, background_color="white", mode="RGB")
wc_lem.generate(text_lem)
plt.figure(figsize=(16, 9))
plt.axis("off")
plt.imshow(wc_lem, interpolation="bilinear")
plt.savefig('../Models/wordcloud_lem.png', transparent=True)
plt.show()

