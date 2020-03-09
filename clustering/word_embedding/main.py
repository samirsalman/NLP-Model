import re
import json
import numpy
from gensim.models import Word2Vec
from pre_processing import speel_checker
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import sklearn.cluster.k_means_ as K_Means

model = Word2Vec.load('./wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')

global multi_dim  # global variable that represents list of phrases vector
global phrases  # global variable that represents list of phrases
global jsonResponse  # global variable that represents jsonBuilder
jsonResponse = []


def new_euclidean_distances(X, Y=None, Y_norm_squared=None, squared=False):
    return cosine_similarity(X, Y)


K_Means.euclidean_distances = new_euclidean_distances


# Take all dates from dataset and write them to file
def writeAllDates(dataset_file):
    with open(dataset_file, 'r') as dataset:
        corpusJSON = json.load(dataset)
        out = open("dates.json", "w+")
        output = {}

        for el in range(len(corpusJSON)):
            output[corpusJSON[el]["data"]] = output.get(corpusJSON[el]["data"], 0) + 1
        out.write(json.dumps(output))
        out.close()
        return


# get all saved dates from file
def getDates(dates_file):
    dates = {}
    file = open(dates_file, "r")
    json_data = json.load(file)
    for el in json_data:
        dates[el] = json_data[el]
    return dates


# from phrase to vector with word embedding
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

    return vector / len(s)


def vectors_similarity(a, b):
    cosine_similarity = numpy.dot(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))
    return cosine_similarity


# function that clean the phrases
def clean_phrases(s):
    s = re.sub(r'[^\w]', ' ', s)
    s = s.replace("è", "essere")
    s = s.replace("sarà", "diventa")
    s = s.replace("morivazione", "motivazione")
    s = s.strip()
    return s.lower()


cols = ["messaggio", "argomento", "chiarimenti"]


# load all phrases from dataset, passing date and column
def load_phrases(path, date_value, col):
    i = 0
    global multi_dim, phrases
    multi_dim, phrases = [], []
    results = open("./results.csv", "w+", encoding='utf-8')
    results.write("f1,f2,v1,v2,sim\n")
    dataset_output = open("./data.csv", "w+", encoding='utf-8')
    dataset_output.write("f,v\n")
    col_value = cols[col]

    with open(path, 'r') as dataset:
        corpusJSON = json.load(dataset)
        for el in range(len(corpusJSON)):
            if corpusJSON[el]["data"] == date_value:
                try:
                    f1 = clean_phrases(corpusJSON[el][col_value])
                    f2 = clean_phrases(corpusJSON[el + 1][col_value])
                    v1 = phrase2vec(f1)
                    v2 = phrase2vec(f2)
                    multi_dim.append(v1)
                    phrases.append(f1)
                    sim = vectors_similarity(v1, v2)
                    results.write(str(f1) + "," + str(f2) + "," + str(v1) + "," + str(v2) + "," + str(sim) + "\n")
                    dataset_output.write(str(f1) + "," + str(v1).rstrip() + "\n")

                except Exception as e:
                    i += 1
                    print(e)

    print("Number of errors: ", i)
    dataset.close()
    results.close()


# create the json structure of response
def write_json(k_means, centroids, date_value, col):
    results = {}
    global phrases
    results["id"] = date_value
    results["col"] = col
    results["cendroids"] = []
    results["elements"] = []

    for i in range(len(k_means.cluster_centers_)):
        print(i)
        results["cendroids"].append({"cluster": i, "phrase": str(phrases[centroids[i]])})

    for i in range(len(k_means.labels_)):
        results["elements"].append({"phrase": phrases[i], "cluster": int(k_means.labels_[i])})

    global jsonResponse
    jsonResponse.append(results)


# write all computed clusters into a json file
def create_json():
    global jsonResponse
    file = open("./clusters_results.json", "w+")
    to_json = json.dumps(jsonResponse)
    file.write(to_json)


# function that compute and create clusters
def make_clusters(K, date_value, col):
    try:
        load_phrases("./dataset.json", date_value, col)
        indxes_of_centroid = []
        X = []
        for el in multi_dim:
            X.append(np.resize(el, 2))
        X = np.array(X)
        print(X[:, 0])
        plt.scatter(X[:, 0], X[:, 1], label='True Position')
        plt.show()
        k_means = KMeans(n_clusters=K, init='random',
                         n_init=10, max_iter=300,
                         tol=1e-04, random_state=0).fit(X)

        plt.scatter(X[:, 0], X[:, 1], c=k_means.labels_, cmap='rainbow')
        plt.show()

        plt.scatter(X[:, 0], X[:, 1], c=k_means.labels_, cmap='rainbow')
        plt.scatter(k_means.cluster_centers_[:, 0], k_means.cluster_centers_[:, 1], s=250, marker='*',
                    c='red', edgecolor='black',
                    label='centroids')
        plt.show()
        test = {i: np.where(k_means.labels_ == i)[0] for i in range(k_means.n_clusters)}
        for i in test.keys():
            indxes_of_centroid.append(test[i][0])
        print(indxes_of_centroid)

        write_json(k_means, indxes_of_centroid, date_value, col)
    except Exception as e:
        print(e)


all_dates = []
all_dates.append(list(getDates("./dates.json").keys()))
print(all_dates)
# make_clusters(3, "3/5/2019", 0)
# make_clusters(3, "3/5/2019", 1)
# make_clusters(3, "3/5/2019", 2)
# create_json()
# writeAllDates("./dataset.json")
for date in all_dates:
       for col_index in range(2):
              make_clusters(3,date,col_index)
create_json()


