import re
import json
import numpy
from gensim.models import Word2Vec
from gensim.models.keyedvectors import Word2VecKeyedVectors

model = Word2Vec.load('./wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')

def phrase2vec(s):
       s = s.split(" ")
       vector = Word2VecKeyedVectors(len(s))
       vector = model.wv[s[0]]
       for i in range(1,len(s)):
              vector = vector + model.wv[s[i]]
       return vector/len(s)

def vectors_similarity(a,b):
       cosine_similarity = numpy.dot(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))
       return cosine_similarity

def clean_phrases(s):
       s = re.sub(r'[^\w]', ' ', s)
       s =s.replace("è", "essere")
       s = s.replace("sarà", "diventa")
       s =s.replace("morivazione", "motivazione")
       return s.lower()


def load_phrases(path):
       i = 0
       with open(path, 'r') as dataset:
              corpusJSON = json.load(dataset)
              for el in range(len(corpusJSON)):
                     try:
                            f1 = clean_phrases(corpusJSON[el]["messaggio"])
                            f2 = clean_phrases(corpusJSON[el+1]["messaggio"])
                            print(f1, f2)
                            vectors_similarity(phrase2vec(f1), phrase2vec(f2))
                     except Exception as e:
                            i += 1
                            print(e)
       print("Number of errors: ", i)


load_phrases("./dataset.json")








