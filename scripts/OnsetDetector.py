'''
Created on Mar 4, 2016

@author: joro
'''
import os
import subprocess




def writeCsv(fileURI, list_):
    from csv import writer
    fout = open(fileURI, 'wb')
    w = writer(fout)
    for row in list_:
        w.writerow(row)
    
    fout.close()

def extractPitch(audioFileURI):
    '''
    extract pitch using local version of pycompmusic and save as csv as input for Nadines algo
    '''
    
    print 'extracting pitch for {}...'.format(audioFileURI)
    from compmusic.extractors.makam import pitch
    extractor = pitch.PitchExtractMakam()
    results = extractor.run(audioFileURI)
    extractedPitchList = results['pitch']
    for i, row in enumerate(extractedPitchList):
        row = row[:-1]
        extractedPitchList[i]=row
    
    outFileURI = os.path.splitext(audioFileURI)[0] + '.pitch.csv'
    writeCsv(outFileURI, extractedPitchList)

def parserNoteOnsetsGrTruth(groundTruthNotesURI, startTime, endTime):

    onsetTimes = []
    from csv import reader
    with open(groundTruthNotesURI) as f:
        r = reader(f, delimiter=' ')
        for row in r:
            onsetTimes.append(float(row[0]) )


    chunkOnsetTimes = []
    
    ######## select part of onset times corresponding to segment
    i = 0
    while startTime > onsetTimes[i]:
        i+=1
        
    while i< len(onsetTimes) and endTime >= onsetTimes[i] :
        chunkOnsetTimes.append(onsetTimes[i] - startTime) 
        i+=1
    return chunkOnsetTimes

def parserNoteOnsets(audioFileURI):
    '''
    with cante
    '''
    
    onsetsURI = os.path.splitext(audioFileURI)[0] + '.notes.csv'
    pitchURI = os.path.splitext(audioFileURI)[0] + '.pitch.csv'
    if not os.path.isfile(onsetsURI):
        if not os.path.isfile(pitchURI):
            extractPitch(audioFileURI)
        
        print 'extracting note onsets for {}...'.format(audioFileURI)
        cante = '/Users/joro/Downloads/cante-beta-csv/DerivedData/cante-static/Build/Products/Debug/cante-static'
        canteCommand = [cante, pitchURI, audioFileURI ]
        pipe= subprocess.Popen(canteCommand)
        pipe.wait()
        
        
    from csv import reader
    onsetTimestamps = []
    with open(onsetsURI) as f:
        r = reader(f)
        for row in r:
            currTs = float( "{0:.2f}".format(float(row[0].strip())) )
#             currTs = round(float(row[0][0]),2)
            onsetTimestamps.append(currTs)
    return onsetTimestamps
    
if __name__ == '__main__':
    
    audioFileURI = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin.wav'
    extractPitch(audioFileURI) 
    
#     onsetTimestamps = parserNoteOnsets(audioFileURI)
