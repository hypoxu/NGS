#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import division, with_statement
'''
Copyright 2010, 陈同 (chentong_biology@163.com).  
Please see the license file for legal information.
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
import sys
import os
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP


desc='''Get sequence of a bed file from genome. 
If strand info is given at the sixth column of bed, it will get strand 
specific sequences. Else all positive strand sequences will be output.

Duplicate names are allowed in the forth column, the program will 
merge sequences in these regions(overlapped part will be only 
considered once). Here we assume **regions with same name should be on 
same strand if there is strand info**.

The output will be printed to file.
'''

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "%prog -i file"
    parser = OP(usage=usages)
    parser.add_option("-i", "--genome-file", dest="filein",
        metavar="FILEIN", help="FATSA formated genome sequence \
file. Separated FATSA fiel for each chromosome in one folder \
will be supported laterly.")
    parser.add_option("-u", "--upper", dest="upper",
        default=0, help="Do you want to keep sequences as \
original[default, or give 0] or uppercase all letters[please give 1]")
    parser.add_option("-b", "--bed-files", dest="bedL",
        help="One bed file or alist of bedfiles separated by \
comma(,) and quoted by quotes like 'bed1,bed2,bed3'.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-d", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------



ATCGdict = {'A':'T','G':'C','T':'A','C':'G',\
    'a':'t','g':'c','t':'a','c':'g','N':'N'}

def readGenome(genome, upper):
    aDict = {}
    key = ''
    for line in open(genome):
        if line[0] == '>':
            if key:
                aDict[key] = ''.join(alist)
            #--------------------------------
            key = line[1:-1]
            alist = []
        else:
            if upper == "Y":
                alist.append(line.upper().strip())
            else:
                alist.append(line.strip())
    #-------------------------------------------
    aDict[key] = ''.join(alist)
    return aDict
#--------------------------------

def getSeq(bed,  aDict, upper, dir):
    '''
    bed: 0-based,  half-open
    '''
    if dir:
        if dir[-1] != '/':
            dir = dir + '/'
        output = dir + os.path.split(bed)[1] + '.upper' + upper + '.fa'
    else:
        output = bed + '.upper' + upper + '.fa'
    fh = open(output, 'w')
    bedDict = {}
    for line in open(bed):
        lineL = line.strip().split('\t')
        name = lineL[3] 
        lineL[1] = int(lineL[1])
        lineL[2] = int(lineL[2])
        if name not in bedDict:
            bedDict[name] = []
        bedDict[name].append(lineL)
        #seq = aDict[chr][start:end]
        #if len(lineL) > 5 and lineL[5] == '-':
        #    strand == '-'
        #else:
        #    strand = '+'
        #    seq = ''.join([ATCGdict[nt] for nt in seq[::-1]])
        #print >>fh, '>%s\n%s' % (name, seq)
    for key,itemL in bedDict.items():
        len_itemL = len(itemL)
        chr = itemL[0][0]
        start1 = itemL[0][1]
        end1   = itemL[0][2]
        if len_itemL == 1:
            seq = aDict[chr][start1:end1]
            if len(itemL[0]) > 5 and itemL[0][5] == '-':
                seq = ''.join([ATCGdict[nt] for nt in seq[::-1]])
        else:
            itemL.sort(key=lambda x: (x[1], x[2]))
            newItemL = []
            for index2 in itemL[1:]:
                start2 = index2[1]
                end2   = index2[2]
                if end1 < start2:
                    newItemL.append((start1, end1))
                    start1 = start2
                    end1   = end2
                elif end2 >= end1 >= start2:
                    newItemL.append((start1, end1))
                    start1 = end1
                    end1   = end2
            newItemL.append((start1,end1))
            #---------------------------------------
            seqL = []
            for index in newItemL:
                seqL.append(aDict[chr][index[0]:index[1]])
            seq = ''.join(seqL)
            if len(itemL[0]) > 5 and itemL[0][5] == '-':
                seq = ''.join([ATCGdict[nt] for nt in seq[::-1]])
        #---------------------------------------------------
        print >>fh, ">%s\n%s" % (key, seq)
    #--------------------------------------
    fh.close()
#-------------------------------------


def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    genome = options.filein
    upper = options.upper
    bedL = [i.strip() for i in options.bedL.split(',')]
    verbose = options.verbose
    debug = options.debug
    #-----------------------------------

    aDict = readGenome(genome, upper)
    for bed in bedL:
        getSeq(bed, aDict, upper, '')

if __name__ == '__main__':
    main()

