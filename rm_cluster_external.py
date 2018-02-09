#!/usr/bin/python

import sys
from subprocess import call
import os
from os import listdir
from Bio import SeqIO

print "rm_cluster_external.py RepeatMaskerOutFile FastaFile PatternFile"

try:
    outfile = sys.argv[1]
except:
    outfile = raw_input("Introduce RepeatMakser OUT file: ")

try:
    fastafile = sys.argv[2]
except:
    fastafile = raw_input("Introduce FASTA file with the reads: ")

try:
    patfile = sys.argv[3]
except:
    patfile = raw_input("Introduce Pattern File: ")

seq_list = {}
pattern = open(patfile).readlines()
for line in pattern:
    seq = line.split()
    seq = seq[1]
    if seq not in seq_list:
        seq_list[seq] = []

data = open(outfile).readlines()
noheader = data[3:]

for n in range(0, len(noheader)):
    info = noheader[n]
    info = info.split()
    this_line = [info[4],info[9]]
    pair_line = []
    if this_line[0][-1] == "1":
        read = info[4][:-1] + "2"
        pair_line = [read,info[9]]
    elif this_line[0][-1] == "2":
        read = info[4][:-1] + "1"
        pair_line = [read,info[9]]
    sub = noheader[n-3:n] + noheader[n+1:n+4]
    up_down = []
    for el in sub:
        sub_info = el.split()
        up_down.append([sub_info[4],sub_info[9]])
    if pair_line not in up_down:
        seq_list[this_line[1]].append(pair_line[0])

call("mkdir sel_reads", shell=True)
os.chdir("sel_reads")

library = "lmig_combo_plus_trna_rmod.fasta"
lib = SeqIO.parse(open("../"+library), "fasta")
annots = []
for s in lib:
    name = str(s.id)
    annot = name.split("#")
    annot = annot[1]
    annot = annot.split("/")
    annot = annot[0]
    annots.append(annot)
annots = set(annots)
annots = list(annots)

annot_sum = open("annot_summary.txt", "w")
annot_sum.write("Sequence\tTotal_reads\t"+"\t".join(annots)+"\n")

cap3_out = open("cap3_stats.txt", "w")
cap3_header = "\t".join(["Sequence","Total_reads","Singletons", "Reads_in_contigs","Number_Contigs","MinCov","MaxCov","MinLen","MaxLen"])
cap3_out.write(cap3_header+"\n")

for el in seq_list:

    print "\n"+el+"\n"

    out = open(el+".txt","w")
    li = seq_list[el]
    li = set(li)
    li = list(li)
    out.write("\n".join(li))
    out.close()

    call("seqtk subseq %s %s.txt > %s.fasta" % ("../"+fastafile, el, el), shell=True)

    sel_reads = list(SeqIO.parse(open(el+".fasta"), "fasta"))
    num_reads = len(sel_reads)

    call("cd-hit-est -T 12 -i %s.fasta -r 1 -M 0 -c 0.8 -o %s.nr80" % (el, el), shell=True)

    print "RepeatMasker -par 12 -no_is -nolow -lib ../%s %s.fasta" % (library, el)
    call("RepeatMasker -par 12 -no_is -nolow -lib ../%s %s.fasta" % (library, el), shell=True)

    annots_dict = {}
    for a in annots:
        annots_dict[a] = 0

    rmout = open(el+".fasta.out").readlines()

    for line in rmout[3:]:
        info = line.split()
        annot = info[10]
        annot = annot.split("/")
        annot = annot[0]
        annots_dict[annot] += 1

    a = []
    for ann in annots:
        a.append(annots_dict[ann])
    a = [str(aa) for aa in a]
    annot_sum.write(el+"\t"+str(num_reads)+"\t"+"\t".join(a)+"\n")
    annot_sum.flush()

    call("rm %s*.tbl %s*.cat %s*.cat.gz %s*.masked %s*.out %s*.log" % (el,el,el,el,el,el), shell=True)

    random = ""

    limit = 10000

    if num_reads >= limit:
        random = ".random"
        call("seqtk sample %s.fasta %s > %s.fasta%s" % (el, str(limit),random))
    call("cap3 %s.fasta%s" % (el,random) , shell=True)
    ace = open(el+".fasta"+random+".cap.ace").readlines()
    nums = []
    lens = []
    for line in ace:
        if line.startswith("CO"):
            info = line.split()
            length = int(info[2])
            number = int(info[3])
            lens.append(length)
            nums.append(number)

    if len(nums) == 0:
        nums = [0]
        lens = [0]

    singlets = list(SeqIO.parse(open(el+".fasta"+random+".cap.singlets"),"fasta"))
    try:
       n_singlets = len(singlets)
    except:
       singlets = [0]
    counts = [el,num_reads,n_singlets,sum(nums),len(nums),min(nums),max(nums),min(lens),max(lens)]
    counts_str = [str(elem) for elem in counts]
    cap3_out.write("\t".join(counts_str)+"\n")
    cap3_out.flush()
    
cap3_out.close()
annot_sum.close()
