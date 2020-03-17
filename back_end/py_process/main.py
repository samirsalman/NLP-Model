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
import sys
from clustering.FastText_embedding import FastText_Embedding

model = Word2Vec.load(
    './py_process/wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')

global multi_dim  # global variable that represents list of phrases vector
global phrases  # global variable that represents list of phrases
global jsonResponse  # global variable that represents jsonBuilder
global persons  # global variable that represents jsonBuilder
jsonResponse = []


def new_euclidean_distances(X, Y=None, Y_norm_squared=None, squared=False):
    return cosine_similarity(X, Y)


K_Means.euclidean_distances = new_euclidean_distances


# Take all dates from dataset and write them to file
def writeAllDates(dataset_file):
    with open(dataset_file, 'r', encoding="utf8") as dataset:
        corpusJSON = json.load(dataset)
        out = open("./tmp_data/dates.json", "w+", encoding="utf8")
        output = {}

        for el in range(len(corpusJSON)):
            output[corpusJSON[el]["dataLezione"]] = output.get(
                corpusJSON[el]["dataLezione"], 0) + 1
        out.write(json.dumps(output))
        out.close()
        return


# get all saved dates from file
def getDates(dates_file):
    dates = {}
    file = open(dates_file, "r", encoding="utf8")
    json_data = json.load(file)
    i = 0
    return json_data


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
    cosine_similarity = numpy.dot(
        a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))
    return cosine_similarity


# function that clean the phrases
def clean_phrases(s):
    s = re.sub(r'[^\w]', ' ', s)
    s = s.replace("è", "essere")
    s = s.replace("età", "eta")
    s = s.replace("sarà", "diventa")
    s = s.replace("variabile ne", "variabile")
    s = s.replace("morivazione", "motivazione")
    s = s.strip()
    return s.lower()


cols = ["messaggio", "argomento", "chiarimenti"]


# load all phrases from dataset, passing date and column
def load_phrases(path, date_value, col):
    i = 0
    global multi_dim, phrases, persons
    multi_dim, phrases, persons = [], [], []
    results = open("./tmp_data/results.csv", "w+", encoding='utf-8')
    results.write("f1,f2,v1,v2,sim\n")
    dataset_output = open("./tmp_data/data.csv", "w+", encoding='utf-8')
    dataset_output.write("f,v\n")
    col_value = cols[col]

    with open(path, 'r', encoding="utf8") as dataset:
        corpusJSON = json.load(dataset)
        for el in range(len(corpusJSON)):
            if corpusJSON[el]["dataLezione"] == date_value:
                try:
                    f1 = clean_phrases(corpusJSON[el][col_value])
                    f2 = clean_phrases(corpusJSON[el + 1][col_value])
                    #f1 = corpusJSON[el][col_value]
                    #f2 = corpusJSON[el + 1][col_value]
                    '''
                    x = get_vector_of_phrase(get_embedding_list_of_message("Spiegazione di bubble sort, selection sort"))
                    y = space_reduce(x, pca)
                    '''
                    v1 = phrase2vec(f1)
                    v2 = phrase2vec(f2) #GETVECTORPHRASE
                    # v1 = FastText_Embedding.space_reduce(FastText_Embedding.get_vector_of_phrase(
                    #     FastText_Embedding.get_embedding_list_of_message(f1)),#TRAINED PCA
                    #      )
                    # v2 = FastText_Embedding.space_reduce(FastText_Embedding.get_vector_of_phrase(
                    #     FastText_Embedding.get_embedding_list_of_message(f2)),#TRAINED PCA
                    #      )

                    multi_dim.append(np.resize(v1, 2))
                    phrases.append(f1)
                    persons.append(corpusJSON[el]["codice"])
                    sim = vectors_similarity(v1, v2)
                    results.write(str(f1) + "," + str(f2) + "," +
                                  str(v1) + "," + str(v2) + "," + str(sim) + "\n")
                    dataset_output.write(
                        str(f1) + "," + str(v1).rstrip() + "\n")

                except Exception as e:
                    i += 1
                    print(e)

    print("Number of errors: ", i)
    dataset.close()
    results.close()


# create the json structure of response
def write_json(k_means, centroids, date_value, col):
    results = {}
    global phrases, persons
    results["id"] = date_value + "-" + str(col)
    results["col"] = col
    results["date"] = date_value
    results["cendroids"] = []
    results["elements"] = []


    for i in range(len(k_means.cluster_centers_)):
        print(i)
        results["cendroids"].append({"cluster": i, "phrase": str(
            phrases[centroids[i]]), "person_id": str(persons[centroids[i]]), "vector":multi_dim[i]})

    for i in range(len(k_means.labels_)):
        results["elements"].append({"phrase": phrases[i], "cluster": int(
            k_means.labels_[i]), "person_id": persons[i], "vector" : multi_dim[i]})

    global jsonResponse
    jsonResponse.append(results)


# write all computed clusters into a json file
def create_json():
    global jsonResponse
    file = open("./tmp_data/clusters_results.json", "w+", encoding="utf8")
    to_json = json.dumps(jsonResponse)
    file.write(to_json)


# function that compute and create clusters
def make_clusters(K, dataset, date_value, col):
    try:
        load_phrases(dataset, date_value, col)
        indxes_of_centroid = []
        X = multi_dim
            #FastText_Embedding.space_reduce(el,#PCA)

        X = np.array(X)
        print(X[:, 0])
        plt.scatter(X[:, 0], X[:, 1], label='True Position')
        # plt.show()
        k_means = KMeans(n_clusters=K, init='random',
                         n_init=10, max_iter=300,
                         tol=1e-04, random_state=0).fit(X)

        plt.scatter(X[:, 0], X[:, 1], c=k_means.labels_, cmap='rainbow')
        # plt.show()

        plt.scatter(X[:, 0], X[:, 1], c=k_means.labels_, cmap='rainbow')
        plt.scatter(k_means.cluster_centers_[:, 0], k_means.cluster_centers_[:, 1], s=250, marker='*',
                    c='red', edgecolor='black',
                    label='centroids')
        # plt.show()
        test = {i: np.where(k_means.labels_ == i)[
            0] for i in range(k_means.n_clusters)}
        for i in test.keys():
            indxes_of_centroid.append(test[i][0])
        print(indxes_of_centroid)

        write_json(k_means, indxes_of_centroid, date_value, col)
    except Exception as e:
        print(e)


dataset_path = ""
if len(sys.argv) == 2:
    dataset_path = sys.argv[1]

all_dates = []
writeAllDates(dataset_path)
getDates(dataset_path)
all_dates.append(list(getDates("./tmp_data//dates.json").keys()))
print(all_dates)
for el in all_dates[0]:
    make_clusters(3, dataset_path, el, 0)
    make_clusters(3, dataset_path, el, 1)
    make_clusters(3, dataset_path, el, 2)
# make_clusters(3, "3/5/2019", 1)
# make_clusters(3, "3/5/2019", 2)
# create_json()
# writeAllDates("./dataset.json")
# for date in all_dates:
#     for col_index in range(2):
#         make_clusters(3, date, col_index)

create_json()
