# SatIntExt
Analysis of SATellite INTernal and EXTernal Illumina reads

## Protocol to extract internal and external read pairs of a repetitives elements

### Definitions

- Internal or homogeneous read pair: Both members with homology to the same repetitive element. They are supposed to be inside a satDNA array.
- External or heterogeneous read pair: One member with homology to a repetitive element and the other one with homology to a different repetitive element. One read is supposed to be inside a satDNA array and the other one is supposed to be outside a satDNA array.

![My image](https://github.com/fjruizruano/SatIntExt/blob/main/internal_external_read_pairs.png)

### 0. Shuffle reads

FASTA files with the reads should be shuffled. You can use a script form the [Velvet assembler](https://github.com/dzerbino/velvet/tree/master/contrib/shuffleSequences_fasta):
```
$ shuffleSequences_fasta.pl file_1.fasta file_2.fasta file_12.fasta
```

The FASTA file should be like this:
```
>seq1/1
AAAAAA
>seq1/2
AAAAAA
>seq2/1
AAAAAA
>seq2/2
AAAAAA
[...]
```

### 1. If necessary, join and replace variant names to get only a name per family.

```
$ ls species*.out > lista_out.txt
$ rm_join_out.py
$ mv test.all.out species.out
$ replace_patterns.py species.out pattern.txt
```

It you don't have a pattern.txt file from the fasta file with the consensus sequences:
```
$ grep ">" references.fasta | sed 's/>//g' | sed 's/#/\t/g' | awk {'print $1 "\t" $1'} > pattern.txt
```

This is how the first line looks after each command element of the pipe:
```
>OdeSat01A-287#Satellite/OdeSat01A-287
OdeSat01A-287#Satellite/OdeSat01A-287
OdeSat01A-287    Satellite/OdeSat01A-287
OdeSat01A-287    OdeSat01A-287
```

After manual edition of the second column to have the same name for each family in the second column, the pattern.txt file looks like this:
```
# OdeSat01A-287   OdeSat01A-287
# OdeSat02A-204   OdeSat02A-204
# OdeSat02B-205   OdeSat02A-204
# OdeSat02C-204   OdeSat02A-204
# OdeSat02D-204   OdeSat02A-204
# OdeSat03A-148   OdeSat03A-148
# OdeSat03B-149   OdeSat03A-148
# OdeSat04A-181   OdeSat04A-181
# ...
```

### 2. Extract annotated reads by RepeatMasker

Remove hits with asterisk (*) from the RepeatMasker OUT file to avoid duplicated hits

```
$ grep -v "*" species.out.fam > species.out.fam.noasterisk
```

Extract and annotate reads, then count occurrences
```
$ rm_getseq_annot.py species.fa species.out.fam.noasterisk 1
```
1 means minimum length of 1 nt.
This step can last few minutes.
Output: >OdeSat01A-287_ID:ILLUMINA:READ/1

```
$ rm_count_matches_monomers.py species.out.fam.noasterisk.fas MinimumLength
```
It counts number of matching nucleotides > n (considered as a complete read, by default 11 nt lower than the read length).
Columns in the output file:
* Annotation: Annotation
* DIM_N: number of complete matches (reads)
* DIM_MON: sum of nt from complete matches
* NODIM_N: number of incomplete matches (reads)
* NODIM_MON: sum of nt from incomplete matches

In a spreadsheet we get the total number of reads with aligning at least 89 nt summing DIM_N and NODIM_N

### 3. Estimate divpeak and RPS

Optionally, you can estimate divpeak (divergence of the maximum peak) and RPS (relative peak size).

![Divpeak](https://github.com/fjruizruano/SatIntExt/blob/main/divpeak_github.png)

For this you need to create a input file with the name of the divsum files considering only families of satellites and the number of nucleotides of the library:
```
species1.out.fam.noasterisk	1010000000
species2.out.fam.noasterisk	1010000000
```

Then, use this text file as input for the script
```
$ divsum_stats.py divsum_size.txt
```

Outputs:
* results.txt: it contains divpeak and rps
* toico.txt: it contains the sum of nucleotides

### 4. Cluster external reads and annotate them

This step is independent of the steps 2 and 3, but required cd-hit-est and cap3 installed.

It extracts external reads separately from all annotations and clusterize them:
```
$ rm_cluster_external.py species.out.fam.noasterisk species.fa pattern.txt
```

It needs an annotation file named "lmig_combo_plus_trna_rmod.fasta". You can modify the script to use another file name.
Please consider that it can last some minutes/few hours.
The script breaks if there are no external reads for a family. In that case remove the satellite where it stops and run again. It jumps analyzed satellites and continue the work.

Outputs:
* annot_summary.txt: Total number of external reads and annotated external reads
* cap3_stats.txt: Assembly of external reads using Cap3
* cdhit_stats.txt: Clustering of external reads using CDHIT

Open annot_summary.txt in a spreadsheet and add the total number of reads from step 2.
You can calculate the Tandem Structure Index: TSI = Internal read pairs/Total read pairs:

