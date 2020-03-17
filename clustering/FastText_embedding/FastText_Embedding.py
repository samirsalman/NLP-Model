#NOTE: IF IT'S YOUR FIRST TIME HERE, PLESE DOWNLOAD THE ITALIAN EMBEDDING VECTORS AT --> https://fasttext.cc/docs/en/crawl-vectors.html
#GO TO MODELS AND DOWNLOAD THE ITALIAN .bin
#UNZIP IT AND MOVE IT INTO YOUR FOLDER
#REMEMBER THAT PATH, WE'LL USE IT

# Import libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import os, re, csv, math, codecs
from subprocess import check_output
import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from nltk.tokenize import RegexpTokenizer
import os, re, csv, math, codecs
from subprocess import check_output
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

nltk.download('stopwords')                             #<-- Download it if it's your first time using it

sns.set_style("whitegrid")
np.random.seed(0)

embed_dim = 300

DATA_PATH = './'                                            #<-- Set your datapath
EMBEDDING_DIR = './'                                        #<-- Set your embedding_path

tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('italian'))
stop_words.update(['.', ',', '"', "'", ':', ';', '(', ')', '[', ']', '{', '}'])

print('loading word embeddings...')
embeddings_index = {}
f = codecs.open(EMBEDDING_DIR+'cc.it.300.vec', encoding='utf-8')
for line in tqdm(f):
    values = line.rstrip().rsplit(' ')
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()
print('found %s word vectors' % len(embeddings_index))

dataset = pd.read_json (DATA_PATH+'dataset.json')

#Visualize word distribution
dataset['mes_len'] = dataset['messaggio'].apply(lambda words: len(words.split(" ")))
max_seq_len = np.round(dataset['mes_len'].mean() + dataset['mes_len'].std()).astype(int)

sns.distplot(dataset['mes_len'], hist=True, kde=True, color='b', label='mes len')
plt.axvline(x=max_seq_len, color='k', linestyle='--', label='max len')
plt.title('comment length'); plt.legend()
plt.show()

def tokenize_word(messaggio):
    
    tokenize_message_list = []
    tokens = tokenizer.tokenize(messaggio)
    filtered = [word for word in tokens if word not in stop_words]
    tokenize_message_list.append(" ".join(filtered))
    
    return tokenize_message_list[0]

def get_embedding_list_of_message(messaggio):
    clear_message = tokenize_word(messaggio)
    
    q = clear_message.split(" ")
    
    embedding_token = []
    for token in q:
        if (embeddings_index.get(token) is None):
            vector = np.random.uniform(-math.sqrt(6/embed_dim),math.sqrt(6/embed_dim), embed_dim)
            embedding_token.append(vector)
        
        else:
            embedding_token.append(embeddings_index.get(token))
    
    return embedding_token


#For a sentence, we add the vectors of the words that compose it

def get_vector_of_phrase(array):
    z = np.zeros(embed_dim)
    for vector in array:
        z = np.sum([z, vector], axis = 0)
    return z

# Using the cosine similarity

def vectors_similarity(a,b):
    cosine_similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    return cosine_similarity

#Create an embeddding_matrix for all the sentences

def get_embedding_matrix(dataset):
    
    emb_matrix = np.array([])
    
    if (emb_matrix.size == 0):
        emb_vector = get_vector_of_phrase(get_embedding_list_of_message(dataset['messaggio'][0]))
        emb_vector = emb_vector.reshape(-1,1).transpose()
        emb_matrix = emb_vector
        
        
    for elem in dataset['messaggio'][1:]:
        emb_vector = get_vector_of_phrase(get_embedding_list_of_message(elem))
        emb_vector = emb_vector.reshape(-1,1).transpose()
        
        emb_matrix = np.concatenate((emb_matrix, emb_vector), axis = 0)
        
    return emb_matrix

emb_matrix = get_embedding_matrix(dataset)                              # <-- a checkpoint

#The emd_matrix cointains, for each word (and sentence), 300 dimension.
#So, we use the PCA algorithm to reduce the dimensions of our vector.

def fit_PCA(arrays_n_dim):
    pca_model = PCA(n_components = 2)
    pca_model.fit(arrays_n_dim)
    
    final_array_2_components = pca_model.transform(arrays_n_dim)
    
    return pca_model, final_array_2_components




def space_reduce(vector_of_phrase, training_pca):
    vector_of_phrase = vector_of_phrase.reshape(-1,1).transpose()
    trained_PCA_array = training_pca.transform(vector_of_phrase)
    
    return trained_PCA_array[0]

pca, arrays_2_dim = fit_PCA(emb_matrix)                                                                         # <-- another checkpoint with test
x = get_vector_of_phrase(get_embedding_list_of_message("Spiegazione di bubble sort, selection sort"))

y = space_reduce(x, pca)

#Plotting the distribution of points

def plot(name, points): 
    
    X_coordinate = []
    Y_coordinate = []


    for coordinate in points:
        X_coordinate.append(coordinate[0])
        Y_coordinate.append(coordinate[1])
    
    fig = plt.figure()
    
    plt.scatter(X_coordinate, Y_coordinate)
    
    plt.title("Points in two dimensions")
    
    dirName = 'plots'
    
    try:                                                                # <-- Create a folder (if it doesn't already exist) for save our plot
        os.mkdir(dirName)
        print("Directory " , dirName,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")
    
    fig.savefig('./plots/'+str(name), dpi=800)
    plt.close(fig)


def plot_with_mex(points, dataset):                                     # <-- Create a interactive plot to show, for each point, its message 

    sentences = []

    for mex in dataset['messaggio']:
        sentences.append(mex)

    X_coordinate = []
    Y_coordinate = []


    for coordinate in points:
        X_coordinate.append(coordinate[0])
        Y_coordinate.append(coordinate[1])

    init_notebook_mode(connected=True)

    data = [
        go.Scatter(
            x=X_coordinate,
            y=Y_coordinate,
            mode='markers',
            text=[i for i in sentences],
        marker=dict(
            size=16,
            color = [len(i) for i in sentences],                        # <-- We color the points differently based on the length of their sentence 
            opacity= 0.8,
            colorscale='Viridis',
            showscale=False
        )
        )
    ]
    layout = go.Layout()
    layout = dict(
                  yaxis = dict(zeroline = False),
                  xaxis = dict(zeroline = False)
                 )
    fig = go.Figure(data=data, layout=layout)
    file = plot(fig, filename='Sentence encode.html')                   # <-- Show the plot into a new webpage


plot('plot', arrays_2_dim)                                              # checkpoint
plot_with_mex(arrays_2_dim, dataset)
