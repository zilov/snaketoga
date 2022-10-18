#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@created: 18.10.2022
#@author: Danil Zilov
#@contact: zilov.d@gmail.com

import argparse
import os
import os.path
from inspect import getsourcefile
from datetime import datetime
import string
import random
import json
import errno

def config_maker(settings, config_file):
    with open(config_file, "w") as fw:
        json.dump(settings, fw)
        print(f"CONFIG IS CREATED! {config_file}")
      
def file_exists(path_to_file):
    if os.path.exists(path_to_file) and os.path.getsize(path_to_file) > 0:
        return path_to_file
    return argparse.ArgumentTypeError(f"{path_to_file} empty or does not exist")

def main(settings):
    
    if settings["dry-run"]:
        snake_dry = "-n"
    else:
        snake_dry = ""

    #Snakemake
    command = f"""
    snakemake --snakefile {settings["execution_folder"]}/workflow/snakefile \
              --configfile {settings["config_file"]} \
              --cores {settings["threads"]} \
              --use-conda \
              --conda-frontend \
              --conda-prefix {settings["execution_folder"]}/config \
                {snake_dry}"""
    print(command)
    os.system(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Snaketoga - snakemake wrapper for TOGA orthologs annotator')
    parser.add_argument("-r", "--reference", help="Reference genome you are going to use.\
        Here human == hg38, mouse = mm10. For others use custom mode.", 
        choices=["human", "mouse", "custom"], default="human",  type=file_exists)
    parser.add_argument("-rg", "--reference-genome", help="Path to softmasked reference genome file in FASTA format", 
                        required=True, type=file_exists)
    parser.add_argument("-a", "--annotation",
                        help="reference genome annotation file in GFF3 or BED12 format", required=False, type=file_exists)
    parser.add_argument("-i", "--isoforms",
                        help="Genes isoforms of reference genome. Read TOGA manual to find file format.",
                        required=False,  type=file_exists)
    parser.add_argument("-u12", 
                        help="U12 sites of reference genome, TSV file. Read TOGA manual to find file format.",
                        required=False, type=file_exists)
    parser.add_argument('-g','--genome', help="Path to softmasked genome FASTA file you're gonna annotate", 
                        required=True, type=file_exists)
    parser.add_argument("-p", "--prefix", help="Prefix of your run, default is a genome name", default=None)
    parser.add_argument('-o','--outdir', help='Path to output directory', required=True)
    parser.add_argument('-t','--threads', help='Number of threads to use [default == 8]', default = 8, type=int)
    parser.add_argument('-d','--dry-run', help='Dry-run', action='store_true')
    args = vars(parser.parse_args())

    mode = args["reference"]
    reference_genome = os.path.abspath(args["reference-genome"])
    annotation = os.path.abspath(args["annotation"])
    u12 = os.path.abspath(args["u12"])
    isoforms = os.path.abspath("isoforms")
    genome = os.path.abspath(args["assembly"])
    threads = args["threads"]
    dry = args["dry-run"]
    outdir = os.path.abspath(args["outdir"])
    prefix = args["prefix"]
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    execution_folder = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))
    execution_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    if not prefix:
        prefix = os.path.splitext(os.path.split(genome)[1])[0]
        random_letters = "".join([random.choice(string.ascii_letters) for n in range(3)])
        config_file = os.path.join(execution_folder, f"config/config_{random_letters}_{execution_time}.yaml")  
    else:
        config_file = os.path.join(execution_folder, f"config/config_{prefix}_{execution_time}.json")
    
    toga_folder = os.path.join(execution_folder, f"TOGA")
    if not os.path.exists(toga_folder):
        print(f"TOGA not found in {execution_folder}! Please download it!")
        raise FileNotFoundError(
             errno.ENOENT, os.strerror(errno.ENOENT), toga_folder)
    
    if mode == "human":
        u12 = os.path.join(toga_folder, "/supply/hg38.U12sites.tsv")
        isoforms = os.path.join(toga_folder, "/supply/hg38.v35.for_toga.isoforms.tsv")
        annotation = os.path.join(toga_folder, "/supply/hg38.v35.for_toga.bed")
    elif mode == "mouse":
        u12 = os.path.join(toga_folder, "/supply/mm10.U12sites.tsv")
        isoforms = os.path.join(toga_folder, "/supply/mm10.v25.for_toga.isoforms.tsv")
        annotation = os.path.join(toga_folder, "/supply/mm10.v25.for_toga.bed")
        
    settings = {
        "reference_genome": reference_genome,
        "annotation": annotation,
        "u12": u12,
        "isoforms": isoforms,
        "genome" : genome,
        "outdir" : outdir,
        "threads" : threads,
        "prefix": prefix,
        "mode" : mode,
        "execution_folder" : execution_folder,
        "dry" : dry,
        "config_file" : config_file
    }
    
    config_maker(settings, config_file)
    main(settings)
