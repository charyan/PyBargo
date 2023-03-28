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

if len(sys.argv) < 2 or (sys.argv[1] not in ["build", "release-build", "run",
                                             "release-run", "init", "clean",
                                             "config", "help", "flags",
                                             "debug"]):
    print("pb: missing command operand\nTry 'pb help' for more information")
    exit(1)

if sys.argv[1] == "--help" or sys.argv[1] == "help" or sys.argv[1] == "-h":
    print("\nUsage: pb [COMMAND]\n\n"
          "    build         Build the current app in debug mode\n"
          "    release-build Build the app in release mode\n"
          "    run           Build and run the app in debug mode\n"
          "    release-run   Build and run the app in release mode\n"
          "    debug         Build the app in debug mode and open in debugger\n"
          "    init [name]   Create project structure\n"
          "    clean         Delete all .o files in build dir and executables\n"
          "    config        Show pb config (defined in pb.toml)\n"
          "    flags         Generate a compile_flags.txt file containing CPP_FLAGS\n"
          "    help          Show this message\n")
    exit(0)


if sys.argv[1] == "init":
    if len(sys.argv) < 3:
        print("Error: No project name given.\nUsage: pb init <project name>")
        exit(1)
    os.mkdir("{}".format(sys.argv[2]))
    fo = open("{}/pb.toml".format(sys.argv[2]), "w+")
    fo.write('''[package]
name = "{}"
package_version = "0.1.0"
pybargo_version = "0.1"

[compiler]
CC = "clang++"
CPP_FLAGS = "-fexperimental-library -std=c++20 -stdlib=libc++ -Wall -Wextra \
-pedantic -Iinclude"
DEBUG_BUILD_FLAGS = "-g -Og"
RELEASE_BUILD_FLAGS="-O2 -s"
RELEASE_OUTPUT_FILENAME="release-app"
DEBUG_OUTPUT_FILENAME="debug-app"

[debugger]
DBG="lldb"
DEBUGGER_RUN_FLAGS="--source-quietly -o run -o exit --"
    '''.format(sys.argv[2]))
    fo.close()
    os.mkdir("{}/src".format(sys.argv[2]))
    os.mkdir("{}/src/{}".format(sys.argv[2], sys.argv[2]))
    os.mkdir("{}/include".format(sys.argv[2]))
    os.mkdir("{}/include/{}".format(sys.argv[2], sys.argv[2]))
    fo = open("{}/src/main.cpp".format(sys.argv[2]), "w+")
    fo.write('''
#include <iostream>

int main() {
    std::cout << "Hello World !" << std::endl;
    return 0;
}
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

if sys.argv[1] == "flags":
    with open("compile_flags.txt", "w") as f:
        output_string = ''
        for flag in data['compiler']['CPP_FLAGS'].split():
            output_string += flag + '\n'
        f.write(output_string)
        f.close()
        exit(0)


def rmBuildDir():
    print("Removing build directory.")
    try:
        os.rmdir("build")
        print("build directory removed.")
    except OSError as e:
        if e.errno == 39:
            print("build directory not empty.")
        else:
            print(e)
            exit(1)


if sys.argv[1] == "clean":
    rm_files = glob.glob("build/**/*.o", recursive=True)
    rm_files += (glob.glob("build/{}".format(data['compiler']
                 ['RELEASE_OUTPUT_FILENAME'])))
    rm_files += (glob.glob("build/{}".format(data['compiler']
                 ['DEBUG_OUTPUT_FILENAME'])))
    if len(rm_files) > 0:
        print("Files to remove:")
        for f in rm_files:
            print("    {}".format(f))
        iput = input("\nDo you want to delete those files ? y/N ")
        if iput == 'y' or iput == 'Y':
            for f in rm_files:
                os.remove(f)
                print("{} deleted".format(f))
            rmBuildDir()
            print("\nFinished. Quitting")
        else:
            print("No files deleted. Quitting.")
    else:
        print("No files to delete.")
        rmBuildDir()
    exit(0)

cpp_files = glob.glob("src/**/*.cpp", recursive=True)
file_str = ' '.join(cpp_files)

cmd = "{} {} {} -o build/".format(data['compiler']['CC'],
                                  data['compiler']['CPP_FLAGS'],
                                  file_str)
cmd_release = cmd + "{} {}".format(data['compiler']['RELEASE_OUTPUT_FILENAME'],
                                   data['compiler']['RELEASE_BUILD_FLAGS'])
cmd_debug = cmd + "{} {}".format(data['compiler']['DEBUG_OUTPUT_FILENAME'],
                                 data['compiler']['DEBUG_BUILD_FLAGS'])
try:
    os.mkdir("build")
except FileExistsError:
    pass

if sys.argv[1] in ["build", "run", "debug"]:
    if os.system(cmd_debug) != 0:
        exit(1)
    if sys.argv[1] == "run":
        exit(os.system("{} {} build/{}".format(data['debugger']['DBG'],
                                               data['debugger']['DEBUGGER_RUN_FLAGS'],
                                               data['compiler']['DEBUG_OUTPUT_FILENAME'])))
    elif sys.argv[1] == "debug":
        exit(os.system("{} build/{}".format(data['debugger']['DBG'],
                                            data['compiler']['DEBUG_OUTPUT_FILENAME'])))
elif sys.argv[1] == "release-build" or sys.argv[1] == "release-run":
    if os.system(cmd_release) != 0:
        exit(1)
    if sys.argv[1] == "release-run":
        exit(os.system("build/{}".format(
            data['compiler']['RELEASE_OUTPUT_FILENAME'])))
