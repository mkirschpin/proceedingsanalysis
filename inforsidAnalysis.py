import proceedingsAnalysis
import pandas as pnd
from pathlib import Path

confname = 'Inforsid'
output_dir = 'output_inforsid_50'
unwantedfile='unwantedV2.csv'
seuil = 50 

file_names = ['../Inforsid/InforSID2014/Actes_INFORSID2014.pdf',
              '../Inforsid/InforSID2015/Actes_INFORSID2015.pdf',
              '../Inforsid/InforSID2016/Actes_INFORSID2016.pdf',
              '../Inforsid/InforSID2017/Actes_INFORSID2017.pdf',
              '../Inforsid/InforSID2018/Actes_INFORSID2018.pdf',
              '../Inforsid/InforSID2019/Actes_INFORSID2019.pdf',
              '../Inforsid/InforSID2020/Actes_INFORSID2020.pdf',
              '../Inforsid/InforSID2021/Actes_INFORSID2021.pdf',
              '../Inforsid/InforSID2022/Actes_INFORSID2022.pdf',
              '../Inforsid/InforSID2023/Actes_INFORSID2023.pdf'] 
years = [ 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 ] 
proceedings = { 'file_name': file_names , 'year': years }

print (proceedings)

dfs = [] 
dfsngram = []

for i in range(len(proceedings['file_name'])):
    print ('handling', proceedings['file_name'][i] , 
           'year', proceedings['year'][i],
           'threshold', seuil)
    
    # traitement de la frequence
    (wordcount,ngramscount) = proceedingsAnalysis.proceedingsProcessing(pdf_file_name = proceedings['file_name'][i],
                           output_dir = output_dir,
                           langues=['french','english'],
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
