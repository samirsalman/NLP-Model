import re
import json
import numpy
from gensim.models import Word2Vec
from gensim.models.keyedvectors import Word2VecKeyedVectors
from gingerit.gingerit import GingerIt

model = Word2Vec.load('./wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')

def phrase2vec(s):
       s = s.split(" ")
       vector = Word2VecKeyedVectors(len(s))
       vector = model.wv[s[0]]
       for i in range(1,len(s)):
              vector = vector + model.wv[s[i]]
       return vector/len(s)

def phrase_similarity(a,b):
       cosine_similarity = numpy.dot(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))
       print(cosine_similarity)

def clean_corpus(s):
       #TODO verificare se un articolo è maschile o femminile e cambiare l' con lo/la
       stringa = re.sub(r'[^\w]', ' ', s)
       stringa=stringa.replace("è", "essere")
       stringa=stringa.replace("sarà", "diventa")
       stringa=stringa.replace("morivazione", "motivazione")
       return stringa.lower()


def carica_frase(path):
       i = 0
       with open(path, 'r') as dataset:
              corpusJSON = json.load(dataset)
              for el in range(len(corpusJSON)):
                     try:
                            frase_1= clean_corpus(corpusJSON[el]["messaggio"])
                            frase_2 = clean_corpus(corpusJSON[el+1]["messaggio"])
                            print(frase_1, frase_2)
                            phrase_similarity(phrase2vec(frase_1), phrase2vec(frase_2))
                     except Exception as e:
                            i+=1
                            print(e)
       print(i)
carica_frase("./dataset.json")








