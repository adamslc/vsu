#!/usr/bin/env python3
import sys

import make
import config as cfg
import clean
import history
import patch
import run
import cmd

import argparse

config = cfg.read_config()
if config == None:
    config = cfg.startup_wizzard()
    cfg.write_config(config)

if config["config_version"] < 2:
    print("vsu config files are for an old version.")
    print(f"You can typically resolve this by running rm -r {config['build_dir']}")
    exit(1)

parser = argparse.ArgumentParser(description="Utility for text-based setup in VSim")
subparsers = parser.add_subparsers(title="Commands", metavar="<command>")

parser_make = subparsers.add_parser("make", help="Create a .in file from a .sdf or .pre file and a set of patches")
parser_make.add_argument("--txpp-args", help="Arguments to be used during the final processing step; useful for doing parameter sweeps", default="")
parser_make.set_defaults(func=make.make)

parser_run = subparsers.add_parser("run", help="Create a .in file and use VSim to run the simulation")
parser_run.add_argument("--echo", help="Sets if the simulation output will be echoed to stdout in addtion to be written to LOG", action=argparse.BooleanOptionalAction, default=False)
parser_run.add_argument("--txpp-args", help="Arguments to be used during the final processing step; useful for doing parameter sweeps", default="")
parser_run.add_argument("--output-dir-override", help="Override where VSim writes output (defaults to --txpp-args)", default="")
parser_run.add_argument("--vorpal-args", help="Arguments to be passed to vorpal or vorpalser", default="")
parser_run.add_argument("--run-parallel", help="Run vorpal in parallel; defaults to serial", action=argparse.BooleanOptionalAction, default=False)
# Set to -2 if simulation should not be restart, and -1 if it should be restart from the last dump
parser_run.add_argument("--restart", help="If a dump number is provided, restart the simulation from that dump. Otherwise, restart from the most recent dump", default=-2, const=-1, nargs='?', type=int, dest='restart_simulation')
parser_run.add_argument("--restart-mismatch", help="Allows a simulation to be restarted with a different input file than was used in the initial run", action=argparse.BooleanOptionalAction, default=False)
parser_run.add_argument("--git-hash", help="Checks that the git repository is clean, or store the git hash in the data output directory", action=argparse.BooleanOptionalAction, default=True)
parser_run.add_argument("--write-script", help="Write shell script to run simulation, instead of actually running the simulation.", action=argparse.BooleanOptionalAction, default=False)
parser_run.set_defaults(func=run.run)

parser_cmd = subparsers.add_parser("cmd", help="Run a shell command in a shell that has sourced the VSim config script")
parser_cmd.add_argument("command", help="The command to be run")
parser_cmd.set_defaults(func=cmd.cmd)

parser_clean = subparsers.add_parser("clean", help="Remove all generated input files")
parser_clean.set_defaults(func=clean.clean)

parser_cleanall = subparsers.add_parser("cleanall", help="Remove all generated input files, and hidden vsu config files; this shouldn't be needed in normal use")
parser_cleanall.set_defaults(func=clean.cleanall)

parser_params = subparsers.add_parser("params", help="Show the build parameters that were used to create the .in file")
parser_params.set_defaults(func=make.params)

parser_update = subparsers.add_parser("update", help="Update .patch files to save the modifications that have been made to input files")
parser_update.set_defaults(func=patch.update_patches)

parser_history = subparsers.add_parser("history", help="Show a summary of the histories for a simulation; VERY BETA RIGHT NOW")
parser_history.set_defaults(func=history.history)

args = parser.parse_args()
config.update(vars(args))
args.func(config)
