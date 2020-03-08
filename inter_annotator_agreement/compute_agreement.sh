#!/usr/bin/env bash

N_OF_ANNOTATORS=11

echo "Computing agreements..."

for i in $(seq 2 $N_OF_ANNOTATORS); do
    # do pos tag
    python3.6 inter_annotator_agreement.py -p 0 -t $i > "./results/pos_tagging/pos_$i.txt"
    
    # do sentiment tag
    python3.6 inter_annotator_agreement.py -e 0 -t $i > "./results/sentiment_tagging/sentiment_$i.txt"
done

# do semantic tag
python3.6 inter_annotator_agreement.py -s 0 > "./results/semantic_tagging/semantic_2.txt"

echo "Done succesfully, results saved in ./results"
