Questo file contiene una descrizione del progetto svolto per il corso
di Natural Language Proccessing (NLP), offerto dal corso di laurea
magistrale dell'università di Tor Vergata nell'anno scolastico
2019/2020.

Il file è stato scritto da Leoanrdo Tamiano il giorno 26-03-2020.

# Idea progettuale
L'idea fondamentale su cui si è basato il progetto è stata quella di
definire una architettura modulare formata da vari componenti per poter
essere utilizzata da zanzotto al fine di visualizzare dei clusters
informativi rispetto alle varie lezioni.

Dato che eravamo incerti sulla qualità delle tecniche di processamento
del linguaggio naturale, abbiamo messo l'enfasi su questa architettura
modulare in modo tale da permettere l'eventuale miglioramento del
modulo di NLP, lasciando però inalterata la restante struttura.

È importante notare come l'architettura definita non è basata solo sul
processamento del dataset a nostra disposizione in questo momento, ma
è pensata con lo scopo di erogare un servizio utile nel tempo. Man
mano quindi che zanzotto fa sue lezioni, il sistema fa tutto da solo e
processa i dati che rende poi disponibili a zanzotto.

# Architettura
L'architettura scelta è divisa in tre moduli principali, che andiamo
adesso a descrivere.

## Parte di NLP
Questo modulo si occupa di processare il dataset fornito dal modulo di
back_end al fine di estrarre delle informazioni utili.

Le informazioni estratte in questo momento sono delle
clusterizzazioni, che vengono effettuate per ogni colonna di ogni
lezione presente nel dataset. 

Al fine di effettuare il clustering dobbiamo passare dalla
rappresentazione simbolica delle frasi a quella vettoriale, e per fare
questo abbiamo utilizzato un semplice word embedding tramite la
libreria word2vec e l'utilizzo di un modello trovato su internet e
disponibile al seguente indirizzo [modello NLP ita](http://hlt.isti.cnr.it/wordembeddings/skipgram_wiki_window10_size300_neg-samples10.tar.gz)

Il risultato di questo modulo (il cluster), viene poi passato al
back_end.

La parte di NLP attualmente implementata è stata principalmente
sviluppata da Simone, Samir e Michele. Samir e Michele hanno poi
provato a migliorare il word embedding effettuato utilizzando un altro
modello già disponibile, ma la loro soluzione deve ancora essere
integrata e testata. Infine, anche Claudio attualmente sviluppando una
soluzione parallela assieme a Valerio per il word embedding che però
cerca di costruire un modello (dizionario) utilizzando i dati del
dataset tramite una pesatura tf-idf.

## Parte di back_end
Questo modulo gestisce il principale flusso di dati tra i vari moduli
dell'architettura. In particolare si occupa di:

1. Scaricare i google forms compilati dagli studenti di zanzotto. 
2. Pre-processare i dati scaricati per poterli processare tramite il modulo di NLP.
3. Salvare il risultato del processamento del modulo di NLP all'interno di un database.
4. Utilizzare degli API endpoints per poter ritornare i dati salvati nel database al front-end.

Per quanto riguarda il primo punto, abbiamo creato un account gmail
chiamato "torvergatanlp1920@gmail.com" e abbiamo chiesto a zanzotto di
condividere il dataset con questo account. Così facendo tutti i file
presenti nel google drive dell'account torvergatanlp1920@gmail.com
possono essere considerati come file da processare.

Per quanto riguarda il DB, abbiamo scelto di utilizzare il servizio di
MongoDB Atlas, che permette di hostare gratis un databse mongoDB per
gestire fino ad un massimo di 512 MB di dati.

Gli API endpoints definiti invece sono i seguenti

| API endpoint    | return value description                                                   |
|-----------------|----------------------------------------------------------------------------|
| /lessons/:date  | ritorna i clusters associati alla lezione tenuta nella data specificata    |
| /lessons/latest | ritorna i clusters associati all'ultima lezione processata                 |
| /students/:id   | ritorna i dati di interesse relativi allo studente con quel particolare id |

Dunque se andiamo in /lessons/01-03-2019 otteniamo la clusterizzazione
per ciascuna delle tree colonne della lezione tenuta il primo marzo
del 2019.

Il back_end è sempre in esecuzione, e si interfaccia con il modulo di
NLP e il modulo del front_end.

La parte di back_end è stata principalmente sviluppata da Leonardo e
da Samir.

## Parte di front_end
Questo modulo gestisce la visualizzazione delle informazioni ottenute
dal server back end e processate dal modulo di NLP.

Il modulo deve ancora essere ultimato. Attualmente comunque il modulo
offre una interfaccia simile alla seguente

TODO: add image here

Come è possibile vedere, l'interfaccia offre la possibilità di
scegliere la data della lezione di interesse, e, una volta scelta,
permette di scegliere una colonna e visualizzare i clusters sia in
forma grafica e sia in forma testuale relativi alla colonna scelta.

La parte di front_end è stata principalmente sviluppata da Samir.

# File Structure
A seguire una breve descrizione sulla struttura delle varie cartelle

| Nome cartella              | Descrizione                                        |
|----------------------------|----------------------------------------------------|
| /notes                     | Contiene degli appunti vari sul progetto           |
| /annotations               | Contiene i dati relativi alle annotazioni          |
| /corpus                    | Contiene un esempio di dataset da processare       |
| /inter_annotator_agreement | Contiene il codice necessario per calcolare l'IA   |
| /pre_processing            | Contiene il codice python per il pre-processing    |
| /clustering                | Contiene il codice python per il clustering        |
| /back_end                  | Contiene il codice nodeJS per il back-end server   |
| /ui                        | Contiene il codice reactJS per il front-end client |


Le cartelle più interessanti però sono **/clustering**, **/back_end**
e **/ui**, che contengono rispettivamente i moduli di NLP, back_end e
front_end.

## /clustering
Le cartelle di interesse qui sono due, e sono **/word_embedding** e **/FastText_embedding**.

La cartella **/word_embedding** contiene il primo word embedding
completato, e quello che attualmente viene utilizzato. Il file di
interesse è il file **main.py**

La cartella **/FastText_embedding** invece contiene il word embedding
che attualmente stanno implementando Simone e Michele.

## /back_end
Le cartelle di interesse qui sono le seguenti

1. /api/routes/, che contiene il codice per i vari API endpoints
   definiti.
   
2. /google_keys/, che contiene i token per accedere al google drive
   dell'account torvergatanlp1920@gmail.com
   
3. /py_process/, che contiene il modulo python (il file main.py) che vogliamo utilizzare
   per effettuare il processamento dei clusters. 
   
4. /tmp_data/, che contiene dei file intermedi che vengono utilizzati
   per interfacciarsi con il modulo di NLP

Il file che contiene la parte principale del server invece è il file **server.js**.

## /ui
TODO: completare la descrizione.


	

# Cose da fare
Ci sono svariati aspetti del progetto che possono essere migliorati.
	
L'idea è quella di fare una release v0.1 in cui funziona tutto, e
successivamente, chi vuole partecipare e migliorare una piccola cosa,
potrà effettuare il fork del progetto per implementare la propria idea
o il proprio miglioramento.

Attualmente alcuni punti di spunto per migliorare il progetto sono i seguenti:

- Nel back_end attualmente i file vengono processati a cadenza
  regolare ogni giorno. Se però il professore prova a visualizzare i
  cluster nello stesso giorno in tiene la lezione, il sistema non
  ritornerà i cluster processati. Un possibile miglioramento è quindi
  quello di forzare il processamento dei dati nel momento in cui si
  effettua una query su una data non ancora processata. 
  
- Attualmente è stato scritto il codice solo per due API endpoints, e
  manca il codice per il processamento dei dati relativi al singolo
  studente, ovvero per l'API endpoint /students/:code. In altre
  parole, scrivere il codice back end per processare i dati che a
  zanzotto interessano relativamente ai singoli studenti.
  
- Procedendo nella stessa direzone del punto precedente, attualmente
  l'interfaccia è stata sviluppata solamente per visualizzare i dati
  dei clusters delle lezioni, e non i dati dei singoli
  studenti. L'idea sarebbe quindi quella di ampliare l'interfaccia per
  visualizzare i dati degli studenti. Notiamo come questo punto
  necessita il completamento del punto precedente.
  
Ovviamente questi sono solo spunti per iniziare a pensare. Ci sono un
sacco di cose da fare e da migliorare, specialmente per quanto
riguarda la parte di NLP.
