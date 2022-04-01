#!/usr/bin/env python3
import sys

import make
import config
import clean
import history

import argparse

vsu_config = config.read_config()
if vsu_config == None:
    vsu_config = config.startup_wizzard()
    config.write_config(vsu_config)

parser = argparse.ArgumentParser(description="Utility for text-based setup in VSim")
subparsers = parser.add_subparsers(title="Commands", metavar="<command>")

parser_make = subparsers.add_parser("make", help="Create a .in file from a .sdf or .pre file and a set of patches")
parser_make.add_argument("--txpp-args", help="Arguments to be used during the final processing step; useful for doing parameter sweeps", default="")
parser_make.set_defaults(func=make.make)

parser_run = subparsers.add_parser("run", help="Create a .in file and use VSim to run the simulation")
parser_run.add_argument("--txpp-args", help="Arguments to be used during the final processing step; useful for doing parameter sweeps", default="")
parser_run.add_argument("--vorpal-args", help="Arguments to be passed to vorpal or vorpalser", default="")
parser_run.add_argument("--run-parallel", help="Run vorpal in parallel; defaults to serial", action=argparse.BooleanOptionalAction, default=False)
parser_run.set_defaults(func=make.run)

parser_clean = subparsers.add_parser("clean", help="Remove all generated input files")
parser_clean.set_defaults(func=clean.clean)

parser_cleanall = subparsers.add_parser("cleanall", help="Remove all generated input files, and hidden vsu config files; this shouldn't be needed in normal use")
parser_cleanall.set_defaults(func=clean.cleanall)

parser_params = subparsers.add_parser("params", help="Show the build parameters that were used to create the .in file")
parser_params.set_defaults(func=make.params)

parser_update = subparsers.add_parser("update", help="Update .patch files to save the modifications that have been made to input files")
parser_update.set_defaults(func=make.update_patches)

parser_history = subparsers.add_parser("history", help="Show a summary of the histories for a simulation; VERY BETA RIGHT NOW")
parser_history.set_defaults(func=history.history)

args = parser.parse_args()
vsu_config.update(vars(args))
args.func(vsu_config)
