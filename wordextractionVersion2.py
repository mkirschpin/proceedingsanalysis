from PyPDF2 import PdfFileReader

import nltk
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk import bigrams

import re
from unidecode import unidecode

import unwantedlist

import pandas as pnd


'''
extracText
extract a pdf into a single string (text)
parameters :
    pdf_file_name='proceedings.pdf' -> pdf file name (including path indication) 
return :
    String text : text extrated from the pdf 
'''
def extracText(pdf_file_name='proceedings.pdf') :
    # text est la variable qui contient le text extrait du pdf
    text = ""
    
    #Read the PDF file
    pdf_reader = PdfFileReader(pdf_file_name)
    
    #Get number of pages in the PDF file
    page_nums = pdf_reader.numPages
    #Iterate over each page number
    for page_num in range(page_nums):
        #Read the given PDF file page
        page = pdf_reader.getPage(page_num)
        #Extract text from the given PDF file page
        text = text + page.extractText()

    # convert text in lowercase
    return text.lower()


'''
cleanUpText
nettoie le texte des mots de ligature et normalize certains caractères (accents, ponctuation...)
    parameters :
        text=''     -> texte qui sera nettoyé 
    return :
        string text -> le texte une fois nettoyé
'''
def cleanUpText (text='') :
    #
    # convert some special characters ("ligature") to their ASCII equivalent
    text = text.replace('\u0060',"'") # accent grave `
    text = text.replace('\u00B4',"'") # accent aigu ´
    text = text.replace('\u2018',"'") # apostrophe "virgule" gauche
    text = text.replace('\u2019',"'") # apostrophe "virgule" droite
    text = text.replace('\u201A',"'") # apostrophe "virgule" bas
    text = text.replace('\u201C','"') # aspas "virgule" gauche
    text = text.replace('\u201D','"') #aspas "virgule" droite 
    text = text.replace('\u201D','"') #aspas "virgule" inférieur 
    text = text.replace('\u00AB','"') # guillemet double gauche 
    text = text.replace('\u00BB','"') # guillement double droite
    text = text.replace('\u2039',"'") # guillemet simple gauche
    text = text.replace('\u203A',"'") #	 guillemet simple droite

    text = text.replace('\u0020'," ") #	 espace simple
    text = text.replace('\u00A0'," ") #	 espace insécable
    text = text.replace('\u2007'," ") #	 espace tabulaire
    text = text.replace('\u2008'," ") #	 espace ponctuation
    text = text.replace('\u2009'," ") #	 espace fine
    text = text.replace('\u200A'," ") #	 espace ultrafine
    text = text.replace('\u200B'," ") #	 espace sans chasse
    text = text.replace('\u202F'," ") #	 espace insécable étroite
    text = text.replace('\u205F'," ") #	 espace moyenne mathématique

    text = text.replace('\u0009'," ") #	 tab

    text = text.replace('\u002D',"-") #	 trait d'union 
    text = text.replace('\u00AD'," ") #	 trait d'union conditionnel 
    text = text.replace('\u1428',"-") #	 trait finale canada  
    text = text.replace('\u2010',"-") #	 trait d'union 
    text = text.replace('\u2011',"-") #	 trait d'union incassable 
    text = text.replace('\u2043',"-") #	 puce trait d'union 
    text = text.replace('\u2014',"-") #	 underscore 

    text = text.replace('\n',' ')

    text = text.replace('\u0020',' ')    # espace
    text = text.replace('\u005F', '-')   # underscore

    split_text = text.split()           # nécessaire pour éviter les doubles espaces
    text = ' '.join(split_text)

    return text

'''
removeUnwanted 
supprime des mots qu'on souhaite ignorer à partir d'une liste de mots.
on va également élimiter tous les mots qui ont des caractères speciaux ou 
des chiffres dedans.

    parameters :
        words=[]            -> liste de mots qui constitue notre texte
        langes=['english']  -> liste des langues dont les stopwords doivent être considérés (NLTK)
        unwantedfile='unwanted.csv' -> fichier csv contenant une liste de mots à ignorer
        abrev               -> liste d'abréviations à ignorer
        ponct               -> liste de signes de ponctuation à ignorer
    return :
        words               -> liste de mots mis à jour 
'''
def removeUnwanted (words=[], langues=['english'], unwantedfile='unwanted.csv', 
            abbrev=["etc.","p.", "et al.", "e.g.","i.e."],
            ponct = [',',';','.','?','!','-',':', '(',')','[',']',"d’","l’","s’","qu’",
        "’",'“', "%","/",'\\'] ) :
    
    # on recupère les stopwords des langues concernées
    stop_words = set()
    nltk.download('stopwords')

    if len(langues) >= 1 : 
        stop_words = set(stopwords.words(langues[0]))
        i = 1
        if len(langues) > 1 :
            stop_words.update(set(stopwords.words(langues[i])))
            i += 1

    # on recupère les unwanted words
    unwanted = unwantedlist.unwantedList(filename=unwantedfile) 

    # on reunit tout ça dans une seule liste
    unwanted.extend(abbrev)
    unwanted.extend(stop_words)
    unwanted.extend(ponct)

    words = list(filter(lambda i: i not in unwanted, words))

    # on élimine les mots avec des caractères non numériques (., -, chiffres, etc.)
    # et les mots de moins de 2 caractères
    asupprimer = []
    for w in words :
        if re.search(r'[^a-zA-Z\s]',unidecode(w)) or len(w)<=2 :
            asupprimer.append(w)

    words = list(filter(lambda i: i not in asupprimer, words))

    return words 


''' 
extractFrequentWords
extrait les "n" mots les plus fréquents d'une liste de mots. Ces mots et leur fréquence
sont enregistrés dans un fichier .csv et un DataFreme au format (index: 'word', columns:'count')
est retourné. 
    parameters :
        words=[]                    -> liste des mots 
        list_size=30                -> nombre de mots qui seront inclus (les n plus préquents)
        file_name='proceedings.csv' ->  fichier où les mots les plus frequents seront enregistrés
                                        (path compris)

    return :
        DataFrame freqDist      -> DataFrame avec les mots les plus fréquents et leur fréquence
'''
def extractFrequentWords( words=[], list_size=30, file_name='proceedings.csv') :

    freqDist = FreqDist(words)
    
    wordcount = pnd.DataFrame(freqDist.most_common(list_size), columns=['word','count']).set_index('word')

    wordcount.to_csv(file_name, sep=';', header=True)

    return wordcount



'''
extractFrequentBigrams
extrait les bigramns les plus fréquents à partir d'une liste de mots. Ces bigrams et leur 
fréquence sont ensuite enregistrés dans un fichier .csv et un DataFrame au format 
(index: n-grams, columns: count) est retourné. 
    parameters :
        words=[]                    -> liste des mots 
        list_size=30                -> nombre de bigrams qui seront inclus (les n plus préquents)
        file_name='proceedings.csv' ->  fichier où les bigrams les plus frequents seront enregistrés
                                        (path compris)

    return :
        DataFrame bigram      -> DataFrame avec les bigrams les plus fréquents et leur fréquence

'''
def extractFrequentBigrams (words=[], list_size=30, file_name='proceedings.csv') :

    bigram = bigrams(words)
    fBigram = FreqDist(bigram)

    ngramcount = pnd.DataFrame(fBigram.most_common(list_size), columns=['n-grams','count']).set_index('n-grams')

    ngramcount.to_csv (file_name, sep=';', header=True)

    return ngramcount
