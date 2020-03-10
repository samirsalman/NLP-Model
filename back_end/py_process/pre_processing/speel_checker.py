from pylanguagetool import api

def speel_checker(word):
    request = api.check(word, api_url='https://languagetool.org/api/v2/', lang='it')

    if(len(request['matches']) > 0):                                        #è stato trovato un errore grammaticale
        list_of_new_values = request['matches'][0]['replacements']
        return list_of_new_values[0]['value']
    else:
        return 0


def check_into_string(sentence):
    for word in sentence.split():
        check = speel_checker(word)
        
        if check != 0:                                                      #la parola i-esima contiene un errore
            sentence = sentence.replace(word, check)                        #e rimpiazziamo le sue occorrenze

    
    return sentence.lower()


