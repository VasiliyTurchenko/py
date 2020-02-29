#!/usr/bin/env python

# keil2cmake.py
# (c) Vasiliy Turchenko 20

import sys
import os
import re
#import strings
from pathlib2 import Path

from collections import namedtuple

import xml.etree.ElementTree as ET

from colorama import init
from colorama import Fore, Back, Style

#debug print control
debug_print_enabled = 1

# includes list
include_dirs = set()

# sources list
source_files = set()

# 
out_file_name = "sources_list.cmake"

# debug print
def debug_print(text):
    if debug_print_enabled == 1:
        print(text)
 
# print usage
def usage():
    print("Usage " + sys.argv[0] + " <Keil_proj_file> " + " <target_path> \n")
    print("Keil_proj_file - Keil project *.uvprojx file")
    print("target_path - path to folder with CMakelists.txt file")

# checks if file exists
# return 0 if no file exists
# return 1 if file exists
def check_file_exists(f):
    if f.is_file():
        return 1
    return 0

# checks if directory exists
# return 0 if no dir exists
# return 1 if dir exists
def check_dir_exists(d):
    if d.is_dir():
        return 1
    return 0

##### XML #####
def trim_XML_braces(text):
    s1 = text.split(">")
    s2 = s1[1].split("<")
    return s2[0]

# parses file entry
def parse_FILE_node(fnode):
    File_entry = namedtuple('File_entry', 'fname ftype fpath')
    fname = ""
    ftype = 0
    fpath = ""
    for s in fnode:
        if s.tag == 'FileName':
            fname = ET.tostring(s)
            fname = trim_XML_braces(fname)
        if s.tag == 'FileType':
            ftype = ET.tostring(s)
            ftype = int(trim_XML_braces(ftype))
        if s.tag == 'FilePath':
            fpath = ET.tostring(s)
            fpath = trim_XML_braces(fpath)
            fpath = fpath.replace("\\", "/")
    retval = File_entry(fname, ftype, fpath)
#    debug_print(retval)
    return retval

# parses group of source files    
def parse_GROUP_node(gnode):
    Group = namedtuple('Group', 'gname files')
    gname = ""
#set of filenames, filetypes, filepaths    
    fileset = list()
    for s in gnode:
        if s.tag == 'GroupName':
            gname = ET.tostring(s)
            gname = trim_XML_braces(gname)
            gname = gname.replace("/", "_")
            gname = gname.replace("\\", "_")
            gname = gname.replace(":", "_")
            gname = gname.replace("-", "_")
            gname = gname.upper()
        if s.tag == 'Files':
            for ss in s:
                if ss.tag == 'File':
                    fileset.append(parse_FILE_node(ss))
        retval = Group(gname, fileset)
#    debug_print(retval)
    return retval

# parsed target options
def parse_TARGET_OPTIONS(opt_node):
    return set()

# parses target
def parse_TARGET(tnode):
#                                  target name
#                                        groups of files in the target
#                                               options for the target
    Target = namedtuple('Target', 'tname tgroups toptions')
    tname = ""
    toptions = set()
    tgroups = list()
    for s in tnode:
        if s.tag == 'TargetName':
            tname = ET.tostring(s)
            tname = trim_XML_braces(tname)
        if s.tag == 'TargetOption':
            toptions = parse_TARGET_OPTIONS(s)
        if s.tag == 'Groups':
            for ss in s:
                if ss.tag == 'Group':
                    newgroup = (parse_GROUP_node(ss))
                    tgroups.append(newgroup)
    retval = Target(tname, tgroups, toptions)
#    debug_print(retval)    
    return retval

# create output file
def check_outfile(n):
    output_file = Path(n)
    if output_file.is_file():
        print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL + "The file " + Style.BRIGHT + n + Style.RESET_ALL + " already exists! Overwrite the existing file (y/n)?")
        if not sys.stdin.readline() == "y\n":
            print("Exiting witout any changes made.")
            exit(-5)
    return output_file

def writeln(f, t):
    f.write(t + "\n")

# write cmake lists of sources to the outfile
def write_lists(ofile, groups):
    for g in groups:
        writeln(ofile, "set\t(GROUP_SRC_" + g.gname)
        for f in g.files:
            comm = ""
            if int(f.ftype) != 1:
                comm = "#"
            writeln(ofile, comm + "\t\t" + f.fpath)
        writeln(ofile, "\t)\n")

# writes LIST_OF_SOURCES variable
def write_LIST_OF_SOURCES(ofile, groups):
    writeln(ofile, "set\t(LIST_OF_SOURCES")
    for g in groups:
        writeln(ofile, "\t\tGROUP_SRC_" + g.gname) 
    writeln(ofile, "\t)\n")

def main():
# check arguments
    if len(sys.argv) < 3:
        usage()
        exit(-1)

    keil_proj_file_n = sys.argv[1]
    debug_print(keil_proj_file_n)
    keil_proj_file = Path(keil_proj_file_n)

    if check_file_exists(keil_proj_file) == 0:
        print(Fore.RED + Style.BRIGHT + "Error!" + Style.RESET_ALL + " Can't find Keil project file " + Style.BRIGHT + str(keil_proj_file) + Style.RESET_ALL)
        exit(-2)

#check is file .uvprojx or not
    spl = os.path.splitext(str(keil_proj_file))
    debug_print(spl)
    if spl[1] != ".uvprojx":
        print("Error! Can't find Keil project file " + spl[0] + ".uvprojx")
        exit(-3)

    cmake_dir_n = sys.argv[2]
    debug_print(cmake_dir_n)
    cmake_dir = Path(cmake_dir_n)
    if check_dir_exists(cmake_dir) == 0:
        print("Error! Can't find target directory " + str(cmake_dir))
        exit(-4)

    tree = ET.parse(str(keil_proj_file))
    root = tree.getroot()
    for child in root:
        if child.tag == 'Targets':
            for child2 in child:
                if child2.tag == 'Target':
                    a = parse_TARGET(child2)
                    debug_print(a)
# generate cmake list for the target
                    ofile = check_outfile(a.tname + "_" + out_file_name)
                    debug_print(ofile)
# #open and reset output file
                    text_file = open(str(ofile), "w+")
# write cmake lists of sources to the outfile
                    write_lists(text_file, a.tgroups)
                    write_LIST_OF_SOURCES(text_file, a.tgroups)
                    text_file.close()
                    print(Fore.GREEN + Style.BRIGHT + "Success!" + Style.RESET_ALL + " File " + Style.BRIGHT + str(ofile) + Style.RESET_ALL + " created.")


###############################################################################
if __name__ == "__main__":
    init()
    main()

########################## E. O. F. ###########################################    
