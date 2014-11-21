#!/usr/bin/python

import sys, getopt
import glob
from os.path import isfile, join, dirname, split
from os import remove
import math
import numpy as np
from pysoundfile import SoundFile

blocklenSec     = 3
RMSpercentage   = 20
NhighestPeak    = 2


def main(argv):
    recurse = False
    textout = True


    try:
        opts, args = getopt.getopt(argv,"hr",["help","recursive"])
    except getopt.GetoptError:
        print("drmeter.py <audiofile or path>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("drmeter.py <audiofile or path>")
            sys.exit()
        elif opt in ("-r", "--recursive"):
            recurse = True
        elif opt in ("-t", "--textout"):
            textout = True

    filelist = []
    for arg in args:
        if isfile(arg)==True:
            filelist.append(arg)

    if textout==True:
        path = dirname(filelist[0])
        textpath = join(path, "{0}_dr.txt".format(split(path)[-1]))
        try:
            f = open(textpath, "x")
        except FileExistsError:
            remove(textpath)
            f = open(textpath, "x")


        dashedline = "".join(["-"[:5]] * 94)


        f.write(dashedline + "\n")
        f.write(" Analyzed folder: {0}\n".format(path))
        f.write(dashedline + "\n")
        f.write(" DR\t\tPeak\t\tRMS\t\tFilename\n")
        f.write(dashedline + "\n\n")
        f.close()

    idx = 0
    for nfile in filelist:
        DR, Peak, RMS = calc_drscore(nfile)
        if idx == 0:
            DR_all = np.zeros((len(filelist),len(DR)))
            DR_all[idx,:] = DR
        else:
            DR_all[idx,:] = DR
        idx+=1

        if textout==True:
            f = open(textpath, "a")
            f.write(" DR{0:.0f}\t\t{1:.2f} dB\t{2:.2f} dB \t{3}\n".format(
                    DR.mean(),
                    10*np.log10(np.power(10,Peak/10).mean()),
                    10*np.log10(np.power(10,RMS/10).mean()),
                    split(nfile)[-1]))
            f.close()



    if textout==True:
        f = open(textpath, "a")
        f.write(dashedline + "\n\n")
        f.write(" Number of files:\t{0:d}\n".format(len(filelist)))
        f.write(" Official DR value:\tDR{0:.0f}\n\n".format(DR_all.mean()))
        f.write("".join(["="[:5]] * 94) + "\n")
        f.close()



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

    print()
    print("DR analysis results:")
    print("====================")
    print(filename)
    print()
    print("     :  ", end="")
    for n in range(Nchannels):
        print(" Chann {0:2d}  :: ".format(n+1), end="")
    print()
    print("Peak :  ", end="")
    for peak in Peak_score_log:
        print("{0:7.2f} dB :: ".format(peak), end="")
    print()
    print("RMS  :  ", end="")
    for rms in RMS_score_log:
        print("{0:7.2f} dB :: ".format(rms), end="")
    print()
    print("DR   :  ", end="")
    for dr in DR_score_log:
        print("{0:7.2f}    :: ".format(dr), end="")
    print()

    return DR_score_log, Peak_score_log, RMS_score_log

if __name__ == "__main__":
    main(sys.argv[1:])