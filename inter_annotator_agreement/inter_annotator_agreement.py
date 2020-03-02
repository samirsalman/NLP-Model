# Made by Leonardo Tamiano & Samir Salman

# ------------------ Imports  ---------------------------------------

from itertools import combinations
from argparse import ArgumentParser

import numpy as np
import math
import json

# global variables

POS_FILENAME       = './annotations/pos_sentiment.json'
SEMANTIC_FILENAME  = './annotations/semantic.json'

ANNOTATION_CLASSES = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN",
                      "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONG", "SYM", "VERB", "X"]

ANNOTATORS      = ["Claudio Santoro", "Fabrizio Tafani", "Francesco Arena",
                   "Dente", "tamiano", "Corridori", "MM", "Paolo Cerrito", "salman",
                   "giorgioni", "Volpi"]

N_OF_ANNOTATORS = len(ANNOTATORS)

CLASSES_TO_HIDE    = []
ID_TO_HIDE_FOR_POS = [239]

# ---------------- Pos tagging analysis ----------------

def parse_json_pos(path, annotators_to_consider=ANNOTATORS):
    f = open(path, "r")
    parsed_json = (json.loads(f.read()))
    annotations = {}
    error = 0
    
    for ann in parsed_json:
        list_of_annotations = []
        try:

            # NOTE: We don't consider annotations regarding id found
            # in array ID_TO_HIDE_FOR_POS and also we only consider
            # annotators found in annotators_to_consider
            if ann['id'] in ID_TO_HIDE_FOR_POS or ann['annotatore'] not in annotators_to_consider:
                continue
            
            for field in ['messaggioTags', 'argomentoTags', 'chiarimentiTags']:
                if ann[field] == None:
                    list_of_annotations.append(["" for x in range(0, len(ann[field]))])
                else:
                    list_of_annotations.append([x for x in ann[field] if x not in CLASSES_TO_HIDE])

            if ann['id'] in annotations:
                annotations[ann['id']][ann['annotatore']] = list_of_annotations
            else:
                annotations[ann['id']] = {ann['annotatore']: list_of_annotations}

        except Exception as e:
            print("None argoument of: ", ann['id'] , ann['messaggioWords'], ann['argomentoWords'], ann['chiarimentiWords'])

    return annotations

def pre_process_pos(path, annotators_to_consider=ANNOTATORS):
    annotations_results = parse_json_pos(path, annotators_to_consider)
    annotators_map = {}

    sorted_keys = list(annotations_results.keys())
    sorted_keys.sort()
    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            annotators_map[ann] = []

    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            for row in annotations_results[x][ann]:
                for tag in row:
                    annotators_map[ann].append(tag)

    return annotators_map

# ---------------- Semantic analysis ----------------

def parse_json_semantic(path, annotators_to_consider=ANNOTATORS):

    f = open(path, "r")
    parsed_json = (json.loads(f.read()))

    annotations = {}
    error = 0
    for ann in parsed_json:

        # NOTE: We don't consider annotations regarding id found
        # in array ID_TO_HIDE_FOR_POS and also we only consider
        # annotators found in annotators_to_consider
        if ann['id'] in ID_TO_HIDE_FOR_POS or ann['annotatore'] not in annotators_to_consider:
            continue
        
        if 'voto' in ann and 'id' in ann and 'annotatore' in ann:
            voto = ann['voto']
            
            id = ann['id']
            id_1, id_2, column = str(id).split("-")
            column = int(column)
            id = id[:-2]
            annotator=ann["annotatore"]

            if id in annotations:
                if annotator in annotations[id]:
                    annotations[id][annotator][column] = voto
                else:
                    annotations[id][annotator] = [-1, -1, -1]
                    annotations[id][annotator][column] = voto
            elif id_2 + "-" + id_1 in annotations:
                id = id_2 + "-" + id_1
                if annotator in annotations[id]:
                    annotations[id][annotator][column] = voto
                else:
                    annotations[id][annotator] = [-1, -1, -1]
                    annotations[id][annotator][column] = voto
            else:
                annotations[id] = {annotator : [-1, -1, -1]}
                annotations[id][annotator][column] = voto

    return annotations

def pre_process_semantic(path, annotators_to_consider=ANNOTATORS):
    annotations_results = parse_json_semantic(path, annotators_to_consider)
    annotators_map = {}
    sorted_keys = list(annotations_results.keys())
    sorted_keys.sort()
    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            annotators_map[ann] = []

    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            for mark in annotations_results[x][ann]:
                annotators_map[ann].append(mark)

    return annotators_map

# ---------------- Sentiment analysis ----------------

def parse_json_sentiment(path, annotators_to_consider=ANNOTATORS):

    f = open(path, "r")
    parsed_json = (json.loads(f.read()))

    annotations = {}
    error = 0
    for ann in parsed_json:

        # NOTE: We don't consider annotations regarding id found
        # in array ID_TO_HIDE_FOR_POS and also we only consider
        # annotators found in annotators_to_consider
        if ann['id'] in ID_TO_HIDE_FOR_POS or ann['annotatore'] not in annotators_to_consider:
            continue        
        
        list_of_annotations = []

        list_of_annotations.append(ann['sentimentArgomento'])
        list_of_annotations.append(ann['sentimentChiarimenti'])

        if ann['id'] in annotations:
            annotations[ann['id']][ann['annotatore']] = list_of_annotations
        else:
            annotations[ann['id']] = {ann['annotatore']: list_of_annotations}

    return annotations

def pre_process_sentiment(path, annotators_to_consider=ANNOTATORS):
    annotations_results = parse_json_sentiment(path, annotators_to_consider)
    annotators_map = {}
    
    sorted_keys = list(annotations_results.keys())
    sorted_keys.sort()
    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            annotators_map[ann] = []

    for x in sorted_keys:
        y = annotations_results[x].keys()
        for ann in y:
            for row in annotations_results[x][ann]:
              annotators_map[ann].append(row)

    return annotators_map

# ------------------ Pos-tagging/Sentiment Agreement for 2 annotators  ---------------------------------------

def basic_agreement(row1, row2, classes, agreement_function):
    # annotator statistics: for each annotetor and for each class we
    # count the number of time that annotator has choosen that class.
    antr_1_stats = {}
    antr_2_stats = {}
    accuracy = 0
    terms = 0
    
    for c in classes:
        antr_1_stats[c] = 0
        antr_2_stats[c] = 0
        
    # check annotations
    for i in range(0, min(len(row1), len(row2))):
        annotation_1 = row1[i].upper()
        annotation_2 = row2[i].upper()

        # check if they both have annotated that word. If not, do not
        # consider it.
        if annotation_1 != "" and annotation_2 != "":
            if annotation_1 == annotation_2:
                accuracy += 1

            antr_1_stats[annotation_1] += 1
            antr_2_stats[annotation_2] += 1
            terms += 1

    # compute relative observed agreement
    accuracy = accuracy / float(terms)
    pe = agreement_function(antr_1_stats, antr_2_stats, classes, terms)
    
    agreement = (accuracy - pe)/(1 - pe)
    return agreement

# compute hypothetical probability of chance agreement described in
# cohen's kappa method
def cohen_kappa_hp(antr_1_stats, antr_2_stats, classes, terms):
    pe = 0
    for c in classes:
        pe += antr_1_stats[c] * antr_2_stats[c]
    pe = pe / float((terms**2))

    return pe

# compute hypothetical probability of chance agreement described in
# scott's pi method
def scott_pi_hp(antr_1_stats, antr_2_stats, classes, terms):
    pe = 0
    for c in classes:
        pe += ((antr_1_stats[c] + antr_2_stats[c])/float(terms))**2

    return pe

# ------------------ Pos-tagging/Sentiment Agreement for multiple annotators  ---------------------------------------

# Implementation of ideas found in
# https://www.wikiwand.com/en/Fleiss%27_kappa
# 
def fleiss_kappa(rows, classes):
    # we need to calculate, for each word and for each category, how
    # many annotators assigned that category for that word.

    # how many annotators do we have?
    n = len(rows)

    # how many subjects do we have at most?
    N_max = len(rows[0])

    # how many classes do we have?
    k = len(classes)

    classes_to_num = {}
    for i in range(0, len(classes)):
        classes_to_num[classes[i]] = i
    
    # matrix[i][j] := number of raters who assigned the i-th subject
    # to the j-th category
    m = np.zeros((N_max, k))
    for i in range(0, N_max):
        for a in range(0, n):
            if i < len(rows[a]) and rows[a][i] != '':
                m[i][classes_to_num[rows[a][i].upper()]] += 1


    # P[i] = extent to which raters agree for the i-th subject
    P = [0] * N_max
    for i in range(0, N_max):
        for j in range(0, k):
            P[i] += m[i][j]**2
            
        P[i] = P[i] - n
        P[i] = (1/float((n * (n-1)))) * P[i]

    # P_mean = mean of the Pi's
    P_mean = 0
    for i in range(0, N_max):
        P_mean += P[i]
    P_mean = P_mean / float(N_max)

                
    # p[j] = proportion of all assignment which were to the j-th category
    p = [0] * k
    for j in range(0, k):
        for i in range(0, N_max):
            p[j] += m[i][j]
        p[j] = p[j] / (float)(N_max*n)
    
    # PE as defined in the wikipedia page
    PE = 0
    for j in range(0, k):
        PE += p[j]**2

    # final agreement
    return (P_mean - PE)/float(1 - PE)


# ------------------ Semantic Agreement for 2 annotators ---------------------------------------

# computes the kendel tau correlation between row1 and row2, where
# row1 and row2 are lists of values between 1 and 5.
def kendell_tau(col1, col2):
    # 1) make table of rankings and order it using the first row.
    data_matrix = np.column_stack([col1, col2])
    ind = np.argsort(data_matrix[:,0])
    data_matrix = data_matrix[ind]
    
    # 2) count number of concordant pairs: for every element of the
    # second row count how many larger elements are below it.
    concordant_pairs_list = []
    column = data_matrix[:,1]

    for i in range(0, len(column)):
        concordant_pairs = 0
        for x in column[i:]:
            if x > column[i]:
                concordant_pairs += 1
        concordant_pairs_list.append(concordant_pairs)
    
    # 3) count number of discordant pairs:
    discordant_pairs_list = []
    column = data_matrix[:,1]

    for i in range(0, len(column)):
        discordant_pairs = 0
        for x in column[i:]:
            if x < column[i]:
                discordant_pairs += 1
        discordant_pairs_list.append(discordant_pairs)

    # 4) sum concordant pair values and discordant pair values
    concordant_value = sum(concordant_pairs_list)
    discordant_value = sum(discordant_pairs_list)

    return (float(concordant_value - discordant_value)) / (float(concordant_value + discordant_value))

# ------------------ Semantic Agreement for multiple annotators ---------------------------------------

# TODO: understand how to extend kendell's tau to multiple annotators.

# ------------------ Main functions ---------------------------------------

def compute_pos_agreement(file_path, annotators=ANNOTATORS):
    print("|--------------- Pos annotation agreement -------------------------|")        
    iaa_pos       = fleiss_kappa(list(pre_process_pos(file_path, annotators).values()),
                                 ANNOTATION_CLASSES)

    print(f"POS for: {annotators}")                
    print("POS: ", iaa_pos)

def compute_sentiment_agreement(file_path, annotators=ANNOTATORS):

    print("|--------------- Sentiment annotation agreement --------------------|")
    iaa_sentiment = fleiss_kappa(list(pre_process_sentiment(file_path, annotators).values()),
                                 ['POSITIVO', 'NEGATIVO', 'NEUTRO'])

    print(f"SENTIMENT for: {annotators}")                    
    print("SENTIMENT: ",iaa_sentiment)

def compute_semantic_agreement(file_path):
    print("|--------------- Semantical annotation agreement ------------------|")
    # compute statistical significance for kendells tau
    
    semantic_results = list(pre_process_semantic(file_path).values())
    n = len(semantic_results[0])

    print(len(semantic_results))
    
    CODE_TO_ANNOTATORS = {
        0: "Santoro",
        1: "Fabrizio Tafani",
        2: "Dente",
        3: "Francesco Arena",
        4: "tamiano",
        5: "Corridori",
        6: "MM",
        7: "salman",
        8: "giorgioni",
        9: "Volpi",
        10: "Paolo Cerrito"
    }

    for pair in combinations(range(0, N_OF_ANNOTATORS), 2):
        i, j = pair

        print(f"Semantic for: {CODE_TO_ANNOTATORS[i], CODE_TO_ANNOTATORS[j]}")

        tau = kendell_tau(
            semantic_results[i],
            semantic_results[j])
        
        z = 3 * tau * math.sqrt(n * (n-1)) / math.sqrt(2 * (2*n + 5))

        print(f"Tau     is: {tau}")
        print(f"Z-value is: {z}")

if __name__ == "__main__":    
    argument_parser = ArgumentParser()
    argument_parser.add_argument("-p", "--pos", dest="pos", help="compute pos tagging agreement")
    argument_parser.add_argument("-e", "--sent", dest="sent", help="compute sentiment tagging agreement")
    argument_parser.add_argument("-s", "--sem", dest="sem", help="compute semantic tagging agreement")
    argument_parser.add_argument("-t", "--tuple", dest="tpl", help="tuple size")    

    args = argument_parser.parse_args()

    # NOTE: assume args.tpl is passed as an integer

    if args.pos and not args.tpl:
        compute_pos_agreement(POS_FILENAME)
        
    elif args.sent and not args.tpl:
        compute_sentiment_agreement(POS_FILENAME)
        
    elif args.sem and not args.tpl:
        compute_semantic_agreement(SEMANTIC_FILENAME)
        
    elif args.pos and args.tpl:
        for t in combinations(ANNOTATORS, int(args.tpl)):
            annotators = list(t)
            compute_pos_agreement(POS_FILENAME, annotators)
        
    elif args.sent and args.tpl:
        for t in combinations(ANNOTATORS, int(args.tpl)):
            annotators = list(t)
            compute_sentiment_agreement(POS_FILENAME, annotators)    
