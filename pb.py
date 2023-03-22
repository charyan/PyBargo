#!/usr/bin/python3.11

# PyBargo : A simple and fast build system for C++
# Copyright (C) 2023 Yannis Charalambidis
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import glob
import sys

if not (sys.version_info[0] == 3 and sys.version_info[1] >= 11):
    print("Python 3.11 or higher needed. Quitting")
    exit(1)

import tomllib

if len(sys.argv) == 1:
    print("pb: missing file operand\nTry 'pb help' for more information")
    exit(1)

if sys.argv[1] == "--help" or sys.argv[1] == "help" or sys.argv[1] == "-h":
    print("\nUsage: pb [COMMAND]\n\n"
          "    build         Compile the current app in debug mode\n"
          "    release-build Compile the app in release mode\n"
          "    run           Compile and run the app in debug mode\n"
          "    release-run   Compile and run the app in release mode\n"
          "    init          Create default pb.toml config\n"
          "    clean         Delete all .o files, debug and release executables\n"
          "    config        Show pb config (defined in pb.toml)\n"
          "    help          Show this message\n")
    exit(1)


if sys.argv[1] == "init":
    fo = open("pb.toml", "w+")
    fo.write('''
[compiler]
CC = "clang++"
CPP_FLAGS = "-fexperimental-library -std=c++20 -stdlib=libc++ -Wall -Wextra -pedantic"
DEBUG_BUILD_FLAGS = "-g -Og"
RELEASE_BUILD_FLAGS="-O2 -s"
RELEASE_OUTPUT_FILENAME="./release-app"
DEBUG_OUTPUT_FILENAME="./debug-app"

[debugger]
DBG="lldb"
DEBUGGER_RUN_FLAGS="--source-quietly -o run -o exit --"
    ''')
    fo.close()
    exit(0)

data = {}

try:
    with open("pb.toml", "rb") as f:
        data = tomllib.load(f)
        f.close()
        if sys.argv[1] == "config":
            for k, v in data.items():
                print("[{}]".format(k))
                for l, w in v.items():
                    print("    {:25} : {}".format(l, w))
                print()
            exit(0)
except FileNotFoundError:
    print("No pb.toml in current directory. Quitting.")
    exit(1)

if sys.argv[1] == "clean":
    rm_files = glob.glob("**/*.o", recursive=True)
    rm_files += (glob.glob("{}".format(data['compiler']['RELEASE_OUTPUT_FILENAME'])))
    rm_files += (glob.glob("{}".format(data['compiler']['DEBUG_OUTPUT_FILENAME'])))
    if len(rm_files) > 0:
        print("Files to remove:")
        for f in rm_files:
            print("    {}".format(f))
        iput = input("\nDo you want to delete those files ? y/N ")
        if iput == 'y' or iput == 'Y':
            for f in rm_files:
                os.remove(f)
                print("{} deleted".format(f))
            print("\nFinished. Quitting")
        else:
            print("No files deleted. Quitting.")
    else:
        print("No files to delete. Quitting")
    exit(0)

cpp_files = glob.glob("**/*.cpp", recursive=True)
file_str = ' '.join(cpp_files)

cmd = "{} {} {} -o".format(data['compiler']['CC'], data['compiler']['CPP_FLAGS'],
                           file_str)
cmd_release = cmd + " {} {}".format(data['compiler']['RELEASE_OUTPUT_FILENAME'],
                                    data['compiler']['RELEASE_BUILD_FLAGS'])
cmd_debug = cmd + " {} {}".format(data['compiler']['DEBUG_OUTPUT_FILENAME'],
                                  data['compiler']['DEBUG_BUILD_FLAGS'])

if sys.argv[1] == "build" or sys.argv[1] == "run":
    if os.system(cmd_debug) != 0:
        exit(1)
    if sys.argv[1] == "run":
        exit(os.system("{} {} {}".format(data['debugger']['DBG'],
                                         data['debugger']['DEBUGGER_RUN_FLAGS'],
                                         data['compiler']['DEBUG_OUTPUT_FILENAME'])))
elif sys.argv[1] == "release-build" or sys.argv[1] == "release-run":
    if os.system(cmd_release) != 0:
        exit(1)
    if sys.argv[1] == "release-run":
        exit(os.system("{}".format(data['compiler']['RELEASE_OUTPUT_FILENAME'])))
