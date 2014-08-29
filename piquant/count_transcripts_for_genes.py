#!/usr/bin/env python

"""Usage:
    count_transcripts_for_genes [--log-level=<log-level>] <gtf-file>

-h --help                 Show this message.
-v --version              Show version.
--log-level=<log-level>   Set logging level (one of {log_level_vals}) [default: info].
<gtf-file>                GTF file containing genes and transcripts.
"""

import collections
import docopt
import gtf
import options as opt
import schema

GTF_FILE = "<gtf-file>"


def get_transcript_to_gene_mappings(gtf_info):
    transcript_to_gene_mappings = {}

    for index, row in gtf_info.iterrows():
        attributes_dict = gtf.get_attributes_dict(row[gtf.ATTRIBUTES_COL])
        transcript = attributes_dict[gtf.TRANSCRIPT_ID_ATTRIBUTE]
        if transcript not in transcript_to_gene_mappings:
            transcript_to_gene_mappings[transcript] = \
                attributes_dict[gtf.GENE_ID_ATTRIBUTE]

    return transcript_to_gene_mappings


def get_transcript_counts_for_genes(transcript_to_gene_mappings):
    transcript_counts = collections.Counter()
    for gene in transcript_to_gene_mappings.values():
        transcript_counts[gene] += 1

    return transcript_counts


# Read in command-line options
__doc__ = opt.substitute_into_usage(__doc__)
options = docopt.docopt(__doc__, version="count_transcripts_for_genes.py")

# Validate command-line options
try:
    opt.validate_log_level(options)
    opt.validate_file_option(options[GTF_FILE], "Could not open GTF file")
except schema.SchemaError as exc:
    exit(exc.code)

# Set up logger
logger = opt.get_logger_for_options(options)

logger.info("Reading GTF file {f}...".format(f=options[GTF_FILE]))
gtf_info = gtf.read_gtf_file(options[GTF_FILE])

logger.info("Extracting transcript to gene mappings...")
transcript_to_gene_mappings = get_transcript_to_gene_mappings(gtf_info)

logger.info("Calculating transcript counts for genes...")
transcript_counts = get_transcript_counts_for_genes(
    transcript_to_gene_mappings)

logger.info("Printing transcript counts for genes...")
print("transcript,gene,transcript_count")
for transcript, gene in transcript_to_gene_mappings.items():
    print("{t},{g},{c}".format(
        t=transcript, g=gene, c=transcript_counts[gene]))
