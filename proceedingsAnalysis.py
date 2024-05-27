'''
Script de traitement de proceedings
Mars 2024
MKP
'''

import wordextractionVersion2
import wordextraction

import spacy

import os

from wordcloud import WordCloud
import matplotlib.pyplot as plt

'''
proceedingsProcessing
traitement d'un pdf contenant un proceedings, analyse de la frequence des mots et des bigrams.
pour chaque proceedings, deux csv sont créés, un pour les mots les plus frequents et l'autre pour les bigrams

parameters :
    pdf_file_name = 'proceedings.pdf'   -> nom du fichier PDF avec le proceedings à traiter (path compris)
    output_dir = 'output'               -> répertoire où les CSV seront enregistrés
    langues=['french','english']        -> langues du proceedings (pour les stopwords)
    unwantedfile='unwanted.csv'         -> liste des mots à ignorer (en plus des stopwords) 
    abbrev=["etc.","p.", "et al.", "e.g.","i.e."]   -> liste d'abbréviations à ignorer
    threshold = 30                      -> seuil de frequence pour les mots et bigrams à garder

return :
    Tuple (wordcount, ngramcount) -> Tuple contenant deux DataFrames, taille indiquée par threshold
                                     un avec les mots les plus frequents, et l'autre avec les
                                     bigramns les plus frequents
                                     
'''
def proceedingsProcessing (pdf_file_name = 'proceedings.pdf',
                           output_dir = 'output',
                           langues=['french','english'],
                           unwantedfile='unwanted.csv', 
                           abbrev=["etc.","p.", "et al.", "e.g.","i.e."],
                           threshold = 30) :
    
    print ('handling',pdf_file_name, 'unwanted :',unwantedfile, 
           'language:', langues, 'output :', output_dir)
    
    # extration du texte
    text = wordextractionVersion2.extracText(pdf_file_name)
    
    # nettoygage caractères speciaux 
    text = wordextractionVersion2.cleanUpText(text)
    
    # analyse du texte (NLP)
    nlp = spacy.load("fr_core_news_sm")

    #lemmatizer
    lemmatizer = nlp.get_pipe("lemmatizer")
    
    #analysis
    nlp.max_length = nlp.max_length*5 
    doc = nlp(text)
    
    # recupère ensemble des mots
    wordset = [(X, X.pos_) for X in doc]
    
    # on supprime les verbes et autres éléments
    unwanted_tag = ['VERB', 'AUX', 'NUM', 'DET', 'ADP', 'CCONJ', 'PUNCT', 'SPACE']
    words = []

    for mot,tag in wordset:
        if not tag in unwanted_tag :
            #words.append(mot.text) #on utilise le lemma
            words.append(mot.lemma_)
            
    # on supprime les mots non désirés
    words = wordextractionVersion2.removeUnwanted (words, 
                                                   langues=langues, 
                                                   abbrev=abbrev,
                                                   unwantedfile=unwantedfile )
 
    # analyse de fréquence des mots
    os.makedirs(output_dir, exist_ok=True)
    output_csv = wordextraction.definefilepath(pdf_file_name=pdf_file_name, 
                                               output_dir=output_dir, 
                                               extension=".wordcount.csv")
    
    wordcount = wordextractionVersion2.extractFrequentWords( words, 
                                                            list_size=threshold, 
                                                            file_name=output_csv)
    
    
    # analyse frequence des bigrams
    output_csv = wordextraction.definefilepath(pdf_file_name=pdf_file_name, output_dir=output_dir, extension=".n-gram.csv")

    ngramcount = wordextractionVersion2.extractFrequentBigrams(words, list_size=threshold, file_name=output_csv)
    
    return (wordcount, ngramcount)


'''
proceedingsVisualisation

création des graphiques de bar et des wordcloud à partir des dataframes

'''
def proceedingsVisualisation (wordcount, ngramcount, 
                              figsize=(20,20), 
                              threshold=30,
                              pdf_file_name='proceedings.pdf', 
                              output_dir='output') :
    
    # creation graphique bar wordcount
    wordcount.plot(kind='bar',figsize=figsize, legend=False)
    output_fig = wordextraction.definefilepath(pdf_file_name=pdf_file_name, 
                                            output_dir=output_dir, 
                                            extension=".wordcount.bar.pdf")
    plt.savefig(output_fig, bbox_inches='tight', pad_inches=1)

    # creation graphique bar bigrams
    ngramcount.plot(kind='bar',figsize=figsize, legend=False)
    output_fig = wordextraction.definefilepath(pdf_file_name=pdf_file_name, 
                                           output_dir=output_dir, 
                                           extension=".ngrams.bar.pdf")
    plt.savefig(output_fig, bbox_inches='tight', pad_inches=1)
    
    
    # creation wordcloud pour les mots (wordcount)
    dico = wordcount.to_dict()['count']

    wc = WordCloud(width=1600, height=800, max_words=threshold, background_color="white").generate_from_frequencies(dico)
    plt.figure(figsize=figsize)
    plt.imshow(wc)

    output_fig = wordextraction.definefilepath(pdf_file_name=pdf_file_name, 
                                            output_dir=output_dir, 
                                            extension=".wordcount.wcloud.pdf")

    plt.savefig(output_fig, bbox_inches='tight', pad_inches=1)
    
    # creation wordcloud pour les bigrams (ngramcount)
    output_fig = wordextraction.definefilepath(pdf_file_name=pdf_file_name, 
                                           output_dir=output_dir, 
                                           extension=".ngram.wcloud.pdf")

    dico_bigram = ngramcount.to_dict()['count']
    dico = {}
    for key in dico_bigram.keys() :
        #print(key, dico_bigram.get(key) )
        k2= str(key[0] + '_' + key[1])
        dico.update({k2:dico_bigram.get(key)})

    wc = WordCloud(width=1600, height=800, max_words=threshold, background_color="white").generate_from_frequencies(dico)

    plt.figure(figsize=figsize)
    plt.imshow(wc)

    plt.savefig(output_fig, bbox_inches='tight', pad_inches=1)
    