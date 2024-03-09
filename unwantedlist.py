''' 
Function unwantedList read a CSV file containing a list of 
unwanted words and returns a list containing all these words. 

@parameter filename= CSV file conting the words (unwanted.csv by default) 
'''
import pandas


def unwantedList(filename='unwanted.csv') :
    dfunwanted = pandas.read_csv(filename, header=[0], delimiter=";")    
    unwanted = dfunwanted[dfunwanted.columns[0]].values.tolist()
    
    return unwanted


