
import sys, getopt
import math
import numpy as np
from pysoundfile import SoundFile

blocklenSec = 3
RMSpercentage = 20
NhighestPeak = 2

testfile = "mylo_xyloto_1ch.wav"

def main(argv):

    recurse = False
    inputfile = "."

    try:
        opts, args = getopt.getopt(argv,"hr",["help","recursive"])
    except getopt.GetoptError:
        print("drmeter.py -i <audiofile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("drmeter.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-r", "--recursive"):
            recurse = True

    filelist = []
    idx = 0
    for arg in args:
        if isfile(arg)==True:
            filelist.append(arg)
            idx+=1

    for nfile in filelist:
        calc_drscore(nfile)




def calc_drscore(filename):

    data = SoundFile(filename)

    NblockLen   = round(blocklenSec*data.sample_rate)
    NblockIdx   = math.ceil(data.frames/NblockLen)
    Nsamples    = data.frames
    Nchannels   = data.channels

    RMS         = np.zeros((NblockIdx,Nchannels))
    Pk          = np.zeros((NblockIdx,Nchannels))

    for nn in range(NblockIdx):
        if nn<NblockIdx:
            curData = data[1+(nn)*NblockLen:1+(NblockLen+(nn)*NblockLen),:]
        else:
            curData = data[1+(nn)*NblockLen:,:]

        for cc in range(Nchannels):
            interim = 2*(np.power(np.abs(curData[:,cc]),2))

            RMS[nn,cc] = math.sqrt(interim.mean());
            Pk[nn,cc]  = max(abs(curData[:,cc]));

    iUpmostBlocks = round(NblockIdx*RMSpercentage*0.01)
    RMS.sort(axis=0)
    Pk.sort(axis=0)
    RMS[:] = RMS[::-1,:]
    Pk[:] = Pk[::-1,:]

    RMS_upmost = RMS[:iUpmostBlocks,:]
    RMS_total = np.sqrt((np.power(RMS,2)).mean(axis=0))

    pre0 = np.power(RMS_upmost,2).sum(axis=0)
    pre1 = np.repeat(iUpmostBlocks, Nchannels, axis=0)
    pre2 = np.sqrt(pre0/pre1)

    DR_score = Pk[NhighestPeak-1,:]/pre2
    RMS_score = RMS_total
    Peak_score = Pk[0,:]

    DR_score_log = 20*np.log10(DR_score);
    RMS_score_log = 20*np.log10(RMS_score);
    Peak_score_log = 20*np.log10(Peak_score);



    print(Peak_score_log)
    print(RMS_score_log)
    print(DR_score_log)

    return DR_score_log

if __name__ == "__main__":
    main(sys.argv[1:])