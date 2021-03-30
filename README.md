# SatIntExt
Analysis of SATellite INTernal and EXTernal Illumina reads

##Protocol to extract internal and external read pairs of a repetitives elements
- Internal read pair: Both members with homology to the same repetitive element. They are supposed to be inside a satDNA array.
- External read pair: One member with homology to a repetitive element and the other one with homology to a different repetitive element. One read is supposed to be inside a satDNA array and the other one is supposed to be outside a satDNA array.

###0. Shuffle reads

FASTA files with the reads should be shuffled. You can use: “shuffleSequences_fasta.pl file_1.fasta file_2.fasta file_12.fasta”. An alternative is to use “rexp_prepare_normaltag.py”. The FASTA file should be like this:

>seq1/1
AAAAAA
>seq1/2
AAAAAA
>seq2/1
AAAAAA
>seq2/2
AAAAAA
[...]

