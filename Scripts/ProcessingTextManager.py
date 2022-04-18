import spacy
import nltk
from nltk.tokenize import RegexpTokenizer
import unidecode


class ProcessingTextManager:
    def __init__(self, enable_verbose=False, enable_lemmatization=True, enable_unicode=True):
        self.verbose = enable_verbose
        self.lemmatization = enable_lemmatization
        self.unicode = enable_unicode
        self.tokenizer = RegexpTokenizer(r'[A-z]\w*')
        self.stopwords = nltk.corpus.stopwords.words('portuguese')
        self.my_stopwords = ["louise"]
        self.ignore_words = []
        self.ignore_words.extend(self.stopwords)
        self.ignore_words.extend(self.my_stopwords)
        self.personalize_stopwords()
        self.lemma = spacy.load("pt_core_news_sm")

    def personalize_stopwords(self):
        self.ignore_words.pop(self.ignore_words.index("não"))

    def personalize_lemmatization(self, wrd):
        if wrd == "não":
            return "nao"
        else:
            return wrd

    def apply_lemmatization(self, wrd):
        result = ""
        for tk in self.lemma(wrd):
            result = tk.lemma_
        result = self.personalize_lemmatization(result)
        return result

    def process_sentence(self, sentence):
        # Tokenizar sem numerais
        aux = self.tokenizer.tokenize(sentence)
        if self.verbose:
            print("Tokenizada {}".format(aux))
        # Converte tudo para caixa baixa
        aux = [word.lower() for word in aux]
        if self.verbose:
            print("Caixa baixa {}".format(aux))
        # Retirar stopwords
        aux = [w for w in aux if w not in self.ignore_words]
        if self.verbose:
            print("Retirar stopwords {}".format(aux))
        # Lemmatization
        if self.lemmatization:
            aux = [self.apply_lemmatization(w) for w in aux]
            if self.verbose:
                print("Lemmatization {}".format(aux))
        # Retirar toda acentuação
        if self.unicode:
            aux = [unidecode.unidecode(w) for w in aux]
            if self.verbose:
                print("Retirar acentuação {}".format(aux))
        # Sentenca transformada
        return aux
