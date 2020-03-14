#!/usr/bin/env python
# coding: utf-8

# In[64]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk

from keras.preprocessing.text import Tokenizer
from tqdm import tqdm
from nltk.corpus import stopwords

from nltk.tokenize import RegexpTokenizer 
import os, re, csv, math, codecs
from subprocess import check_output

nltk.download('stopwords')

sns.set_style("whitegrid")
np.random.seed(0)

embed_dim = 300
MAX_NB_WORDS = 100000
tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('italian'))
stop_words.update(['.', ',', '"', "'", ':', ';', '(', ')', '[', ']', '{', '}'])


# In[10]:


print('loading word embeddings...')
embeddings_index = {}
f = codecs.open('C:/Users/symmy/Desktop/cc.it.300.vec', encoding='utf-8')
for line in tqdm(f):
    values = line.rstrip().rsplit(' ')
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()
print('found %s word vectors' % len(embeddings_index))


# In[18]:


dataset = pd.read_json(r'C:/Users/symmy/Desktop/dataset.json', encoding='latin-1')


# In[19]:


dataset


# In[20]:


#visualize word distribution
dataset['mes_len'] = dataset['messaggio'].apply(lambda words: len(words.split(" ")))
max_seq_len = np.round(dataset['mes_len'].mean() + dataset['mes_len'].std()).astype(int)

sns.distplot(dataset['mes_len'], hist=True, kde=True, color='b', label='mes len')
plt.axvline(x=max_seq_len, color='k', linestyle='--', label='max len')
plt.title('comment length'); plt.legend()
plt.show()


# In[26]:


def tokenize_word(messaggio):
    
    tokenize_message_list = []
    tokens = tokenizer.tokenize(messaggio)
    filtered = [word for word in tokens if word not in stop_words]
    tokenize_message_list.append(" ".join(filtered))
    
    return tokenize_message_list[0]


# In[27]:


print(tokenize_word("E' una giornata, che non mi piace, piovosa"))


# In[61]:


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
        


# In[68]:


def get_vector_of_phrase(array):
    temp_vector = np.zeros(embed_dim)
    for vector in array:
        temp_vector = np.sum([temp_vector, vector], axis = 0)
    return temp_vector

    


# In[69]:


def vectors_similarity(a,b):
    cosine_similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return cosine_similarity


# In[80]:


vectors_similarity(get_vector_of_phrase(get_embedding_list_of_message("interessante lo studio dell informatica")), 
                   get_vector_of_phrase(get_embedding_list_of_message("incitamento allo studio dell informatica")))


# In[ ]:





# In[ ]:




