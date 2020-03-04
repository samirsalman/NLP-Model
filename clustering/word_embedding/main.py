import re
import json
import numpy
from gensim.models import Word2Vec
from gensim.models.keyedvectors import Word2VecKeyedVectors

model = Word2Vec.load('./wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')


def phrase2vec(s):
       s = s.split(" ")
       vector = model.wv[s[0]]
       for i in range(1, len(s)):
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
       results = open("./results.csv","w+")
       results.write("f1,f2,sim\n")
       with open(path, 'r') as dataset:
              corpusJSON = json.load(dataset)
              for el in range(len(corpusJSON)-1):
                     try:
                            f1 = clean_phrases(corpusJSON[el]["messaggio"].strip())
                            f2 = clean_phrases(corpusJSON[el+1]["messaggio"].strip())
                            sim = vectors_similarity(phrase2vec(f1), phrase2vec(f2))
                            print("Phrase 1: ", f1, "\nPhrase 2:", f2, "\n", "Similarity: ", sim)
                            results.write(str(f1.strip()) + "," + str(f2.strip()) + ","+str(sim) + "\n")
                     except Exception as e:
                            i += 1
                            print(e)
       print("Number of errors: ", i)
       results.close()


def create_our_vocab():
       i = 0
       sentences = []
       with open("./dataset.json", 'r') as dataset:
              corpusJSON = json.load(dataset)
              for el in range(len(corpusJSON)):
                     try:
                            sentences.append(clean_phrases(corpusJSON[el]["messaggio"]).split(" "))
                            sentences.append(clean_phrases(corpusJSON[el]["argomento"]).split(" "))
                            sentences.append(clean_phrases(corpusJSON[el]["chiarimenti"]).split(" "))

                     except Exception as e:
                            i += 1
                            print(e)
       print("Number of errors: ", i)
       return sentences

#model.build_vocab(sentences=create_our_vocab(), update=True)

load_phrases("./dataset.json")








