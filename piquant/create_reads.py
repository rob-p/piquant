#!/usr/bin/python

# TODO: add logging

"""Usage:
    create_reads prepare_read_dirs [--log-level=<log-level> --out-dir=<out_dir> --num-fragments=<num-fragments> --params-file=<params-file> --read-length=<read-lengths> --read-depth=<read-depths> --paired-end=<paired-ends> --error=<errors> --bias=<biases> <transcript-gtf-file> <genome-fasta-dir>]
    create_reads create_reads [--log-level=<log-level> --out-dir=<out_dir> --params-file=<params-file> --read-length=<read-lengths> --read-depth=<read-depths> --paired-end=<paired-ends> --error=<errors> --bias=<biases>]
    create_reads check_reads [--log-level=<log-level> --out-dir=<out_dir> --params-file=<params-file> --read-length=<read-lengths> --read-depth=<read-depths> --paired-end=<paired-ends> --error=<errors> --bias=<biases>]

-h --help                        Show this message.
-v --version                     Show version.
--log-level=<log-level>          Set logging level (one of {log_level_vals}) [default: info].
--out-dir=<out-dir>              Parent output directory to which read directories will be written [default: output].
--num-fragments=<num-fragments>  Flux Simulator parameters will be set to create approximately this number of fragments [default: 1000000000].
-f --params-file=<params-file>   File containing specification of read-lengths, read-depths and end, error and bias parameter values to create reads for.
-l --read-length=<read-lengths>  Comma-separated list of read-lengths to create reads for.
-d --read-depth=<read-depths>    Comma-separated list of read-depths to create reads for
-p --paired-end=<paired-ends>    Comma-separated list of True/False strings indicating whether paired-end reads should be created.
-e --error=<errors>              Comma-separated list of True/False strings indicating whether reads should be created with errors.
-b --bias=<biases>               Comma-separated list of True/False strings indicating whether reads should be created with sequence bias.
<transcript-gtf-file>            GTF formatted file describing the transcripts to be simulated.
<genome-fasta-dir>               Directory containing per-chromosome sequences as FASTA files.
"""

import docopt
import flux_simulator as fs
import ordutils.log as log
import ordutils.options as opt
import os.path
import parameters
import prepare_read_simulation as prs
import process
import schema
import sys

LOG_LEVEL = "--log-level"
LOG_LEVEL_VALS = str(log.LEVELS.keys())
OUTPUT_DIRECTORY = "--out-dir"
NUM_FRAGMENTS = "--num-fragments"
PARAMS_FILE = "--params-file"
PREPARE_READ_DIRS = "prepare_read_dirs"
CREATE_READS = "create_reads"
CHECK_READS = "check_reads"
TRANSCRIPT_GTF_FILE = "<transcript-gtf-file>"
GENOME_FASTA_DIR = "<genome-fasta-dir>"

# Read in command-line options
__doc__ = __doc__.format(log_level_vals=LOG_LEVEL_VALS)
options = docopt.docopt(__doc__, version="create_reads v0.1")

# Validate command-line options
param_values = None

try:
    opt.validate_dict_option(
        options[LOG_LEVEL], log.LEVELS, "Invalid log level")
    opt.validate_dir_option(
        options[OUTPUT_DIRECTORY], "Output parent directory does not exist")
    options[NUM_FRAGMENTS] = opt.validate_int_option(
        options[NUM_FRAGMENTS],
        "Number of fragments must be a positive integer",
        nonneg=True)
    opt.validate_file_option(
        options[PARAMS_FILE],
        "Parameter specification file should exist",
        nullable=True)

    if options[PREPARE_READ_DIRS]:
        opt.validate_file_option(
            options[TRANSCRIPT_GTF_FILE], "Transcript GTF file does not exist")
        opt.validate_dir_option(
            options[GENOME_FASTA_DIR], "Genome FASTA directory does not exist")

    param_values = parameters.validate_command_line_parameter_sets(
        options[PARAMS_FILE], options, ignore_params=[parameters.QUANT_METHOD])
except schema.SchemaError as exc:
    exit("Exiting. " + exc.code)


def get_reads_dir(**params):
    return options[OUTPUT_DIRECTORY] + os.path.sep + \
        parameters.get_file_name(**params)


def check_reads_directory(**params):
    reads_dir = get_reads_dir(**params)
    should_exist = options[CREATE_READS] or options[CHECK_READS]
    if should_exist != os.path.exists(reads_dir):
        sys.exit("Reads directory '{d}' should ".format(d=reads_dir) +
                 ("" if options[CREATE_READS] else "not ") + "already exist.")


def prepare_read_simulation(**params):
    reads_dir = get_reads_dir(**params)
    prs.create_simulation_files(
        reads_dir, options[TRANSCRIPT_GTF_FILE], options[GENOME_FASTA_DIR],
        options[NUM_FRAGMENTS], **params)


def create_reads(**params):
    run_dir = get_reads_dir(**params)
    process.run_in_directory(run_dir, './run_simulation.sh')


def check_completion(**params):
    reads_dir = get_reads_dir(**params)
    reads_file = fs.get_reads_file(
        params[parameters.ERRORS],
        'l' if params[parameters.PAIRED_END] else None)
    reads_file_path = reads_dir + os.path.sep + reads_file
    if not os.path.exists(reads_file_path):
        run_name = os.path.basename(reads_dir)
        logger.error("Run " + run_name + " did not complete.")


# Set up logger
logger = log.get_logger(sys.stderr, options[LOG_LEVEL])

to_execute = [check_reads_directory]

if options[PREPARE_READ_DIRS]:
    to_execute.append(prepare_read_simulation)
elif options[CREATE_READS]:
    to_execute.append(create_reads)
elif options[CHECK_READS]:
    to_execute.append(check_completion)

parameters.execute_for_param_sets(to_execute, **param_values)
