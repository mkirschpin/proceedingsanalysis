import proceedingsAnalysis
import pandas as pnd
from pathlib import Path

confname = 'percom'
output_dir = 'output_percom_50'
unwantedfile='unwantedV3.csv'
seuil = 50 

file_names = ['../PERCOM-COMOREA/PERCOM2014/PERCOM2014.pdf',
              '../PERCOM-COMOREA/PERCOM2015/PERCOM2015.pdf',
              '../PERCOM-COMOREA/PERCOM2016/PERCOM2016.pdf',
              '../PERCOM-COMOREA/PERCOM2017/PERCOM2017.pdf',
              '../PERCOM-COMOREA/PERCOM2018/PERCOM2018.pdf',
              '../PERCOM-COMOREA/PERCOM2019/PERCOM2019.pdf',
              '../PERCOM-COMOREA/PERCOM2020/PERCOM2020.pdf',
              '../PERCOM-COMOREA/PERCOM2021/PERCOM2021.pdf',
              '../PERCOM-COMOREA/PERCOM2022/PERCOM2022.pdf' ]#,
#              '../Inforsid/InforSID2023/Actes_INFORSID2023.pdf'] 
years = [ 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022 ] #, 2023 ] 
proceedings = { 'file_name': file_names , 'year': years }

print (proceedings)

dfs = [] 
dfsngram = []

for i in range(len(proceedings['file_name'])):
    print ('handling', proceedings['file_name'][i] , 
           'year', proceedings['year'][i],
           'threshold', seuil)
    
    # traitement de la frequence
    (wordcount,ngramscount) = proceedingsAnalysis.proceedingsProcessing(
                           pdf_file_name = proceedings['file_name'][i],
                           output_dir = output_dir,
                           langues=['english'],
                           unwantedfile=unwantedfile, 
                           threshold = seuil)

    print (wordcount.head(10))
    print (ngramscount.head(10))
        
    # visualisation 
    print('creating visualisaion...')
    proceedingsAnalysis.proceedingsVisualisation (wordcount, ngramscount, 
                              figsize=(15,15), threshold=seuil,
                              pdf_file_name=proceedings['file_name'][i], 
                              output_dir=output_dir) 

    # on ajoute les résultats aux DFs
    wordcount['source'] = proceedings['file_name'][i]
    wordcount['year'] = proceedings['year'][i]
    dfs.append(wordcount)
    
    ngramscount['source'] = proceedings['file_name'][i]
    ngramscount['year'] = proceedings['year'][i]
    dfsngram.append(ngramscount)    
    
 
 # saving word count results   
fullwordcount = pnd.concat(dfs, join='outer')
print (fullwordcount.sample(10))
print (fullwordcount.describe())

csv_file = str(Path(output_dir).joinpath((confname+'wordcount.csv')))
print ('saving wordcount results on',csv_file)
fullwordcount.to_csv(csv_file, sep=';', header=True)

# saving bigrams results
fullngramcount = pnd.concat(dfsngram, join='outer')
print (fullngramcount.sample(10))
print (fullngramcount.describe())


csv_file = str(Path(output_dir).joinpath((confname+'ngramcount.csv')))
print ('saving ngramcount results on',csv_file)
fullngramcount.to_csv(csv_file, sep=';', header=True)
