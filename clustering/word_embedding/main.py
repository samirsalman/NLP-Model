import re
import json
import numpy
import progressbar
from gensim.models import Word2Vec
from pre_processing import speel_checker
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt

model = Word2Vec.load('./wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')
global multi_dim
global phrases
global date

def phrase2vec(s):
       s = s.split(" ")
       try:
              vector = model.wv[s[0]]
       except Exception as e:
              word = speel_checker.speel_checker(s[0])
              if type(word) is not int:
                     word = word.lower()
                     vector = model.wv[word]
                     print("Word corrected")
              else:
                     vector = model.wv[""]

       for i in range(1, len(s)):
              try:
                     vector = vector + model.wv[s[i]]
              except Exception as e:
                     word = speel_checker.speel_checker(s[i])
                     if type(word) is not int:
                            word = word.lower()
                            vector = vector + model.wv[word]
                            print("Word corrected")
                     else:
                            vector += model.wv[""]

       return vector/len(s)

def vectors_similarity(a,b):
       cosine_similarity = numpy.dot(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))
       return cosine_similarity

def clean_phrases(s):
       s = re.sub(r'[^\w]', ' ', s)
       s = s.replace("è", "essere")
       s = s.replace("sarà", "diventa")
       s = s.replace("morivazione", "motivazione")
       s = s.strip()
       return s.lower()


def load_phrases(path):
       i = 0
       global multi_dim,phrases
       multi_dim = []
       phrases = []
       results = open("./results.csv","w+", encoding='utf-8')
       results.write("f1,f2,v1,v2,sim\n")
       dataset_output = open("./data.csv", "w+", encoding='utf-8')
       dataset_output.write("f,v\n")

       bar = progressbar.ProgressBar(maxval=14, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
       bar.start()

       with open(path, 'r') as dataset:
              corpusJSON = json.load(dataset)
              for el in range(len(corpusJSON)):
                     if(el==0):
                            global date
                            first = corpusJSON[el]["data"]
                            date = first
                     if(el!=0):
                            if corpusJSON[el]["data"] != first:
                                   bar.finish()
                                   return
                     if el%10==0:
                            bar.update(i + 1)
                     try:
                            print(first)
                            f1 = clean_phrases(corpusJSON[el]["messaggio"])
                            f2 = clean_phrases(corpusJSON[el+1]["messaggio"])
                            v1 = phrase2vec(f1)
                            v2 = phrase2vec(f2)
                            multi_dim.append(v1)
                            phrases.append(f1)
                            sim = vectors_similarity(v1, v2)
                            results.write(str(f1) + "," + str(f2) + "," + str(v1) + ","+ str(v2) + ","+str(sim) + "\n")
                            dataset_output.write(str(f1) + "," + str(v1).rstrip() + "\n")

                     except Exception as e:
                            i += 1
                            print(e)
       print("Number of errors: ", i)
       bar.finish()
       dataset.close()
       results.close()


def write_json(k_means, centroids):
       results = {}
       global phrases
       results["id"] = date
       results["cendroids"] = []
       results["elements"] = []

       for i in range(len(k_means.cluster_centers_)):
              print(i)
              results["cendroids"].append({"cluster": i, "phrase": str(phrases[centroids[i]])})

       for i in range(len(k_means.labels_)):
              results["elements"].append({"phrase": phrases[i], "cluster": k_means.labels_[i]})

       file = open("./clusters_results.json", "w+")
       to_json = json.dumps(results)
       file.write(to_json)


def make_clusters(K):
       load_phrases("./dataset.json")
       indxes_of_centroid = []
       X = []
       for el in multi_dim:
              X.append(np.resize(el,2))
       X=np.array(X)
       print(X[:,0])
       plt.scatter(X[:, 0],X[:, 1], label='True Position')
       plt.show()
       k_means = KMeans(n_clusters=K ,init='random',
           n_init=10, max_iter=300,
           tol=1e-04, random_state=0).fit(X)
       plt.scatter(X[:,0], X[:,1], c=k_means.labels_, cmap='rainbow')
       plt.show()

       plt.scatter(X[:,0], X[:,1], c=k_means.labels_, cmap='rainbow')
       plt.scatter(k_means.cluster_centers_[:,0] ,k_means.cluster_centers_[:,1], s=250, marker='*',
           c='red', edgecolor='black',
           label='centroids')
       plt.show()
       test = {i: np.where(k_means.labels_ == i)[0] for i in range(k_means.n_clusters)}
       for i in test.keys():
              indxes_of_centroid.append(test[i][0])
       print(indxes_of_centroid)

       write_json(k_means,indxes_of_centroid)


make_clusters(3)



