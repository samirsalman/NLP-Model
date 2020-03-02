import json
import spacy

nlp = spacy.load("it_core_news_sm")

with open('dataset.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

count = 0

for p in data:
	p["id"] = count
	p["messaggioWords"] = []
	p["messaggioTags"] = []
	p["messaggioMorf"] = []
	p["argomentoWords"] = []
	p["argomentoTags"] = []
	p["argomentoMorf"] = []
	p["chiarimentiWords"] = []
	p["chiarimentiTags"] = []
	p["chiarimentiMorf"] = []

	count += 1
	
	args1 = nlp(p['messaggio'])
	for token in args1:
		p["messaggioWords"].append(token.text)
		p["messaggioTags"].append(token.pos_)
		p["messaggioMorf"].append(token.tag_)
    
	args2 = nlp(p['argomento'])
	for token in args2:
		p["argomentoWords"].append(token.text)
		p["argomentoTags"].append(token.pos_)
		p["argomentoMorf"].append(token.tag_)
    
	args3 = nlp(p['chiarimenti'])
	for token in args3:
		p["chiarimentiWords"].append(token.text)
		p["chiarimentiTags"].append(token.pos_)
		p["chiarimentiMorf"].append(token.tag_)
    
#print(data)

with open(r'./results/results.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)