#!/usr/bin/python

"""Usage:
    count_transcripts_for_genes <gtf-file>

-h --help     Show this message.
-v --version  Show version.
<gtf-file>    GTF file containing genes and transcripts.
"""

from docopt import docopt
from schema import SchemaError

import ordutils.options as opt
import pandas as pd

GTF_FILE = "<gtf-file>"

TRANSCRIPT_COL = "transcript"
GENE_COL = "gene"
TRANSCRIPT_COUNT_COL = "transcript_count"

# Read in command-line options
options = docopt(__doc__, version="count_transcripts_for_genes.py")

# Validate command-line options
try:
    opt.validate_file_option(options[GTF_FILE], "Could not open GTF file")
except SchemaError as exc:
    exit(exc.code)

transcript_to_gene = {}

gtf = pd.read_csv(options[GTF_FILE], sep='\t', header=None)

for index, row in gtf.iterrows():
    attributes = row[8].split(';')
    transcript = attributes[1].split()[1][1:-1]
    if transcript not in transcript_to_gene:
        gene = attributes[0].split()[1][1:-1]
        transcript_to_gene[transcript] = gene

transcript_count = {}
for transcript, gene in transcript_to_gene.items():
    transcript_count[gene] = transcript_count.get(gene, 0) + 1

print TRANSCRIPT_COL + "," + GENE_COL + "," + TRANSCRIPT_COUNT_COL
for transcript, gene in transcript_to_gene.items():
    print("{t},{g},{c}".format(t=transcript, g=gene, c=transcript_count[gene]))