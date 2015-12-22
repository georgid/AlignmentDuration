'''
Created on Dec 11, 2015

@author: joro
'''
from Phoneme import Phoneme


def testIsVowel():
    phonemeVowel = Phoneme('i') 
    isVowel = phonemeVowel.isVowelJingju()
    
    if isVowel:
        print 'yes!'
    else: 
        print 'is not vowel'
        
        

if __name__ == '__main__':
    testIsVowel()