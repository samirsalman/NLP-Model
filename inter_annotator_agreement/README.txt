Nel file inter_annotator_agreement.py è presente lo scripy python che
calcola i vari agreements utilizzando i dati presenti nei file
postagRipulti.json, che contiene sia il pos tagging che la sentiment
analysis, e il file semantica.json, che contiene l'annotazione
semantica delle frasi.

Nella cartella results/ sono presenti i risultati, divisi per tipo di
annotazione: pos-sentiment-semantic. I risultati del pos tagging e
della sentiment analysis sono poi ulteriormente divisi in base al
numero di annotatori scelti per il calcolo. Ad esempio il file
pos_2.txt conterrà l'agreement relativo al pos tagging effettuato da
ogni coppia.

Il file compute_agreement.sh contiene un file per calcolare
velocemente tutti i tipi di agreement se si effettuano dei cambiamenti
nello script inter_annotator_agremeent.py
