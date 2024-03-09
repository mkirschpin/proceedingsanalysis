from PyPDF2 import PdfFileReader
import nltk
from nltk.corpus import stopwords
import unwantedlist
from collections import Counter
from nltk import ngrams
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import re
import pandas



'''
Function readTextFromPDF extracts the text from a PDF file
and cleans it from page numbers, stopwords and unwanted words. 
'''
def extracTextFromPDF(pdf_file_name='proceedings.pdf', unwantedfile='unwanted.csv') :
        
    # text est la variable qui contient le text extrait du pdf
    text = ""
    
    #Open the file in binary mode for reading
    with open(pdf_file_name, 'rb') as pdf_file:
        #Read the PDF file
        pdf_reader = PdfFileReader(pdf_file)
        #Get number of pages in the PDF file
        page_nums = pdf_reader.numPages
        #Iterate over each page number
        for page_num in range(page_nums):
            #Read the given PDF file page
            page = pdf_reader.getPage(page_num)
            #Extract text from the given PDF file page
            text = text + page.extractText()
            
    # convert text in lowercase
    text = text.lower()
    
    # convert some special characters ("ligature") to their ASCII equivalent
    text = text.replace('\uFB00','ff')
    text = text.replace('\uFB01','fi')
    text = text.replace('\uFB02','fl')
    text = text.replace('\uFB03','ffi')
    text = text.replace('\uFB04','ffl')
    
    # deletes page number and any other non-alpha characteres
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # remove stopwords
    
    # word_tokenize accepts a string as an input, not a file.
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    #unwanted = ['doi', 'http', 'https', 'springer','eds', 'org', 'lncs', 'vol', 'fig', 'international', 'conference']
    unwanted = unwantedlist.unwantedList(filename=unwantedfile) 

    # Use this to read file content as a stream:
    filteredtext = ""
    words = text.split()
    for r in words:
        if not r in stop_words:
            if not r in unwanted:
                if len(r)>2:
                    filteredtext = filteredtext + r + " "
    

    # return the text once filtered 
    return filteredtext 


''' 
Création d'un Path avec la bonne extension et dans le bon répertoire 
à partir d'un fichier .pdf
'''
def definefilepath(pdf_file_name='proceedings.csv', output_dir='output', extension='.csv'):
    csv_file_name = Path(pdf_file_name).name.replace('.pdf',extension)
    outdir_csv = Path(output_dir).joinpath(csv_file_name)
    return outdir_csv
 
    

'''
Création d'un wordcount et des n-grams à partir d'un texte filtré. 
Les résultats sont enregistrés dans deux fichiers .csv
'''
def extractcountngrams(filteredtext, pdf_file_name='proceedings.csv', output_dir='output') :
    
    wordcount = Counter(filteredtext.split()).most_common()
    
    wordcountDF = pandas.DataFrame(wordcount, columns=['word', 'count'])
    #print(wordcountDF.head(10))

    outdir_csv = definefilepath(pdf_file_name=pdf_file_name, output_dir=output_dir, extension=".wordcount.csv")
    
    wordcountDF.to_csv(outdir_csv,index=False, sep=';', header=True)
     
    output = list(ngrams(filteredtext.split(), 2))
    #print(output)
    
    ngramcount = Counter(output).most_common()
    #print(ngramcount[:50])
    
    df = pandas.DataFrame(ngramcount, columns=['n-grams','count'])

    print(df.describe())
    
    outdir_csv = definefilepath(pdf_file_name=pdf_file_name, output_dir=output_dir, extension=".n-gram.csv")

    df.to_csv(outdir_csv,index=False, sep=';', header=True)
    
    return wordcountDF, df
    
    
'''
Fonction d'aide pour la création d'un tuple avec un mot et sa fréquence
'''
def convertTuple(tup):
    # les mots du n-gram sont des tuples, cette fonction les convertit en "mot1_mot2"
    return str(tup[0] + '_' + tup[1]) 


'''
Tentative de création d'un wordcloud à partir d'un DataFrame au format [ngram, count].
On récupére uniquement les mots dont le count est suppérieur au seuil (threshold). 
'''
def createwordcloud(df, threshold=40, length=50, pdf_file_name='proceedings.pdf', output_dir='output') :
    
   print('Creating wordcloud of', threshold,'words')
   print(df[df['count']>threshold])
 
   listetext=[]
   for i in df[df['count']>threshold]['n-grams'] :
       listetext.append(convertTuple(i))
    
   print(listetext)
   unique_string=(" ").join(listetext) 
   
   wordcloud = WordCloud(background_color = 'white', max_words = length).generate(unique_string)
   
   plt.figure(figsize=(12,10))
   plt.imshow(wordcloud)
   plt.axis("off")
   
   output_fig = definefilepath(pdf_file_name=pdf_file_name, output_dir=output_dir, extension=".wordcloud.png")
   plt.savefig(output_fig)



'''
Tentative de création d'un graphique de bar avec les n-grams les plus utilisés 
à partir d'un DataFrame au format [ngram, count].
On récupére uniquement les mots dont le count est suppérieur au seuil (threshold). 
'''
def createBar(df, threshold=40, figsize=(20,10), pdf_file_name='proceedings.pdf', output_dir='output') :
    
    df[df['count']>threshold].set_index(['n-grams']).plot(kind="bar", figsize=figsize)
    
    output_fig = definefilepath(pdf_file_name=pdf_file_name, output_dir=output_dir, extension=".bar.pdf")
    plt.savefig(output_fig, bbox_inches='tight', pad_inches=1)
