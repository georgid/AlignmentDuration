'''
Created on Dec 11, 2015

@author: joro
'''
from PhonemeJingju import PhonemeJingju


def testIsVowel():
    phonemeVowel = PhonemeJingju('i') 
    isVowel = phonemeVowel.isVowelJingju()
    
    if isVowel:
        print 'yes!'
    else: 
        print 'is not vowel'
        
        

if __name__ == '__main__':
    testIsVowel()