import pandas as pd
import re
from pandas import DataFrame
import math
import sys

#a function that normalizes names to CamelCase
def normalize_names(unnormalized_name):
    if isinstance(unnormalized_name, basestring): #DO NORMAL PROCESS
        
        words = unnormalized_name.split(' ')
        lowerCaseWords = []
        for word in words:
            lowerWord = word.lower()
            lowerCaseWords.append(lowerWord)
        
        wordsWithFirstCapitalized = []
        for word in lowerCaseWords:

            if len(word) > 0: #check for empty words
                firstCharacter = word[0]
                upperCaseFirstCharacter = firstCharacter.upper()
                everyLetterAfterFirst = word[1:]
                wordWithFirstLetterCapitalized = upperCaseFirstCharacter + everyLetterAfterFirst
                wordsWithFirstCapitalized.append(wordWithFirstLetterCapitalized)
            else:
                pass
        
        normalizedName = ' '.join(wordsWithFirstCapitalized)
        
        normalizedName = fix_saint_mount_etc(normalizedName)
        
        return normalizedName
        
    else: #if it is not a string it is nan and we return ''
        return ''

def vlookup(normedLocation, citiesToMarketsDict):
    if normedLocation not in citiesToMarketsDict:
        return 'NA'
    else:
        return citiesToMarketsDict[normedLocation]

def fix_saint_mount_etc(name):
    #Fix Mt., St., Ft.
    if isinstance(name, basestring):
        coorectedNameMt = re.sub('Mt.', 'Mount', name)
        coorectedNameFtAndMt = re.sub('Ft.', 'Fort', coorectedNameMt)
        coorectedNameFtAndMtAndSt = re.sub('St.', 'Saint', coorectedNameFtAndMt)
        return coorectedNameFtAndMtAndSt
    else:
        return ''

#Take all entries in the state field.  Remove erroneous spaces and other characters.  
#Properly map abbreviations to correct state name
def fixLabel(rawLabel, stateDict):
    if isinstance(rawLabel, basestring):
        
        #strip out all non alpha/space characters
        
        labelWithoutErroneousSpaces = re.sub("^\s+|\s+$", "", rawLabel, flags=re.UNICODE)
        
        properStateName = ''
        if len(labelWithoutErroneousSpaces) == 2:
            upperCaseStateAbbrev = labelWithoutErroneousSpaces.upper()

            if upperCaseStateAbbrev in stateDict:
                properStateName = stateDict[upperCaseStateAbbrev]
            else:
                properStateName = 'abbreviationNotFound'
        else:
            correctedStateName = normalize_names(labelWithoutErroneousSpaces)
            properStateName = correctedStateName
            
        return properStateName

    else:
        return ''


#
####
#######python
##########
#######
####
#


def create_normalized_name(df):
	df['FirstNameCapitalized'] = df['First Name'].apply(lambda x: normalize_names(x))
	df['LastNameCapitalized'] = df['Last Name'].apply(lambda x: normalize_names(x))
	df['NormalizedName'] = df['FirstNameCapitalized'] + df['LastNameCapitalized']
	return df

def normalizedNameConcat(df):
	df['FirstLastAdminMarket'] = df['FirstNameCapitalized'] + df['LastNameCapitalized'] + df['Admin_Market']
	df['FirstLastMailChimp'] = df['FirstNameCapitalized'] + df['LastNameCapitalized'] + df['MailChimp_Market']
	return df

def properState(df):
    stateDataframe = pd.read_csv('/Users/anna/Desktop/KiraBabadookovna/stateAbrv.csv')
    stateDict = dict(zip(stateDataframe['Abbreviation'], stateDataframe['State']))

    df['properState'] = df['State'].apply(lambda x: fixLabel(x, stateDict))
    return df

def NormalizedLocationColumn(df):
    df['CityCapitalized'] = df['City'].apply(lambda x: normalize_names(x))
    df['CityStateConcat'] = df['CityCapitalized'] + df['properState']
    return df

def VlookupMarket(df, citiesToMarketsData):
    citiesToMarketsDictionary = dict(zip(
    CitiesToMarketsData['ConCat'], #THIS IS THE DICTIONARY KEY
    CitiesToMarketsData['Market'])) #THIS IS THE DICTIONARY VALUE

    df['DisplayMarket'] = df['CityStateConcat'].apply(lambda x: vlookup(x, citiesToMarketsDictionary))
    return df

def MailChimpMarketMatch(df):
	print 'doing mailchimp to market'
	MailChimpMarketDictionary = dict(zip(
    Market_name_data['DisplayMarket'],
    Market_name_data['Mailchimp'])) 
	df['MailChimp_Market'] = df['DisplayMarket'].apply(lambda x: vlookup(x, MailChimpMarketDictionary)) 
	return df

def AdminMarketMatch(df):
	AdminMarketDictionary = dict(zip(
    Market_name_data['DisplayMarket'],
    Market_name_data['Admin']))
	df['Admin_Market'] = df['DisplayMarket'].apply(lambda x: vlookup(x, AdminMarketDictionary))
	return df

def fixMT_ST_FT(df):
	df['City'] = df['City'].apply(lambda x: fix_saint_mount_etc(x))
	return df

def create_admin_concat_column(df):
	df['concat'] = df['FirstNameCapitalized'] + df['LastNameCapitalized'] + df['Admin Market']
	return df





#LOAD IN ALL DATA
#pathToSpreadsheet = sys.argv[1]
#pathToOutput = sys.argv[2]

pathToSpreadsheet = '/Users/anna/Desktop/WorkDoc0429.csv'
pathToMarketNames = '/Users/anna/Desktop/KiraBabadookovna/Market_Names.csv'
pathToCitiesToMarkets = '/Users/anna/Desktop/KiraBabadookovna/citiesToMarkets.csv'
#pathToAdminExport = '/Users/anna/Desktop/KiraBabadookovna/AdminExport.csv'
#pathToMailChimpExport = '/Users/anna/Desktop/KiraBabadookovna/MailChimpExport.csv'

Data = pd.read_csv(pathToSpreadsheet)
Market_name_data = pd.read_csv(pathToMarketNames)
CitiesToMarketsData = pd.read_csv(pathToCitiesToMarkets)
#Admin_Export = pd.read_csv(pathToAdminExport)
#MailChimp_Export = pd.read_csv(pathToMailChimpExport)

#Create column NormalizedName
Data = create_normalized_name(Data)
print 'creating normalized names'

#correct FT and MT
Data = fixMT_ST_FT(Data)
print 'correcting FT, MT, and ST'

#Fix state names
Data = properState(Data)

#create column NormalizedLocation
Data = NormalizedLocationColumn(Data)
print 'creating a column normalized location'

#vlookup to match cities and states to display markets
Data = VlookupMarket(Data, CitiesToMarketsData)

#vlookup to match MailChimp Market to Admin Market
Data = AdminMarketMatch(Data)
print 'matching admin market'

#vlookup to match display market to MailChimp Market
Data = MailChimpMarketMatch(Data)
print 'marching mailchimp market'

#Create the concat column
#Data = create_concat_column(Data)
#print 'creting concat? column'


#Concat First name, last name, admin market and concat First name, last name, MailChimp market
Data = normalizedNameConcat(Data)
print 'concat normalized names with Admin and MC Markets'

#


print 'writing data to output'
Data.to_csv('~/Desktop/WorkDoc0429processed.csv')








