'''
Created on Mar 4, 2016

@author: joro
'''
import os



def extractPitch(audioFileURI):
    '''
    extract pitch using local version of pycompmusic and save as csv as input for Nadines algo
    '''
    
    from compmusic.extractors.makam import pitch
    extractor = pitch.PitchExtractMakam()
    results = extractor.run(audioFileURI)
    extractedPitchList = results['pitch']
    
    from csv import writer
    fout = open(os.path.splitext(audioFileURI)[0] + '.pitch.csv', 'wb')
    w = writer(fout)
    for entry in extractedPitchList:
        w.writerow(entry[:-1])
    fout.close()

def parserNoteOnsets(audioFileURI):
    from csv import reader
    onsetTimestamps = []
    with open(os.path.splitext(audioFileURI)[0] + '.notes.csv') as f:
        r = reader(f)
        for row in r:
            currTs = float( "{0:.2f}".format(float(row[0].strip())) )
#             currTs = round(float(row[0][0]),2)
            onsetTimestamps.append(currTs)
    return onsetTimestamps
    
if __name__ == '__main__':
    
    audioFileURI = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin_0_20.88.wav'
#     extractPitch(audioFileURI) 
    onsetTimestamps = parserNoteOnsets(audioFileURI)
    print onsetTimestamps
