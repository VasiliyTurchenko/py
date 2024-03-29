#!/usr/bin/env python
# -*- coding: cp1251 -*-

# keil2cmake.py
# (c) Vasiliy Turchenko 19-Mar-2023

import sys
from sys import exit
import os
import re
#import strings
from pathlib2 import Path

from collections import namedtuple

import xml.etree.ElementTree as ET

from colorama import init
from colorama import Fore, Back, Style
from string import whitespace

# flag that we are on python3
py3 = 0

# debug print control
debug_print_enabled = 0
#
out_file_name = "sources_list.cmake"
exec_name = "EXEC_NAME"
cmake_dir = os.curdir

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
    s1 = str(text).split('>')
    s2 = str(s1[1]).split('<')
    return s2[0]

##### XML #####


def trim_XML_braces2(text):

    text = text.strip()

    s1 = str(text).split('>')

#    print(">>> s1 ")
#    print(s1)

    s2 = str(s1[1]).split('<')
#    print(">>> s2 ")
#    print(s2)

    retval = s2[0].replace("'", "")
#    print(">>> s2[0] ")
#    print(retval)
    return retval

# recursive function


def rec_opt(node):
    retval = {}
    try:
        iterator = iter(node)
    except TypeError:
        # not iterable
        print("not iterable")
    else:
        # iterable
        for s in node:
            key = s.tag
            val = ET.tostring(s)
            val = trim_XML_braces(val)
            retval[key] = val
#            debug_print(str(key) + " = "+ str(retval[key]))
            retval.update(rec_opt(s))
    return retval

# file/group option detect


def proc_opt(node, opt_name):
    retval = rec_opt(node)
#    print(retval)
    return retval

# keil project file types
# 1 - c file
# 2 - asm file
# 3 - object file
# 4 - library file
# 5 - text file
# 6 - custom file
# 7 - c++ file
# 8 - image file

# parses file entry


def parse_FILE_node(fnode):
    File_entry = namedtuple('File_entry', 'fname ftype fpath fopt')
    fname = ""
    ftype = 0
    fpath = ""
    fopt = {}
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
        if s.tag == 'FileOption':
            #            debug_print("file option detected")
            fopt = proc_opt(s, "FileOption")
    retval = File_entry(fname, ftype, fpath, fopt)
#    debug_print(retval)
    return retval

# parses group of source files


def parse_GROUP_node(gnode):
    Group = namedtuple('Group', 'gname files gopt')
    gname = ""
    gopt = {}
# set of filenames, filetypes, filepaths
    fileset = list()
    for s in gnode:
        if s.tag == 'GroupName':
            gname = ET.tostring(s)
            gname = trim_XML_braces(gname)
            gname = gname.replace(" ", "_")
            gname = gname.replace("/", "_")
            gname = gname.replace("\\", "_")
            gname = gname.replace(":", "_")
            gname = gname.replace("-", "_")
            gname = gname.upper()
        if s.tag == 'Files':
            for ss in s:
                if ss.tag == 'File':
                    fileset.append(parse_FILE_node(ss))
        if s.tag == 'GroupOption':
            #            debug_print("group option detected")
            gopt = proc_opt(s, "GroupOption")
        retval = Group(gname, fileset, gopt)
#    debug_print(retval)
    return retval


# dig into xml hierarchy
# we need to go deeper
# tag_list - list of tags to traverse through
def dig_in(tag_list, node):
    L = len(tag_list)
    found = 0
    curr_node = node
    i = 0
#    debug_print("L = " + str(L))
    while i < L:
        found = 0
#       debug_print("i = " + str(i))
        for a in curr_node:
            #            debug_print (type(node))
            if a.tag == tag_list[i]:
                i = i + 1
                curr_node = a
                found = 1
#               debug_print (a.tag + " <> " + tag_list[i - 1] + " i = " + str(i))
                break
        if found == 0:
            # tags did not match
            break
    if (i == L) and (found == 1):
        #        debug_print ("dig_in(): found: " + ET.tostring(curr_node))
        return 1, curr_node
    else:
        #        debug_print ("dig_in(): not found")
        return 0, node

# patch an XMLtree oddity in python3


# parsed target options
def parse_TARGET_OPTIONS(opt_node):
    retval = {}
    dev = opt_node.findall("./TargetCommonOption/Device")
    print(dev[0])
    mcu = ET.tostring(dev[0])
    mcu = trim_XML_braces(mcu)
    print(mcu)
    retval['MCU'] = mcu

# extract C defines
    dig_list = ['TargetArmAds', 'Cads', 'VariousControls', 'Define']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        cdefs = trim_XML_braces2(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : cdefs = " + cdefs)
        retval['TARGET_C_DEFINES'] = cdefs
# extract C undefines
    dig_list = ['TargetArmAds', 'Cads', 'VariousControls', 'Undefine']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        cundefs = trim_XML_braces2(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : cundefs = " + cundefs)
        retval['TARGET_C_UNDEFINES'] = cundefs

# extract ASM defines
    dig_list = ['TargetArmAds', 'Aads', 'VariousControls', 'Define']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        adefs = trim_XML_braces2(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : adefs = " + adefs)
        retval['TARGET_ASM_DEFINES'] = adefs

# extract ASM undefines
    dig_list = ['TargetArmAds', 'Aads', 'VariousControls', 'Undefine']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        aundefs = trim_XML_braces2(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : aundefs = " + aundefs)
        retval['TARGET_ASM_UNDEFINES'] = aundefs

# extract C include dirs
    dig_list = ['TargetArmAds', 'Cads', 'VariousControls', 'IncludePath']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        c_inc = trim_XML_braces(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : c_inc = " + c_inc)
        retval['C_INC_DIRS'] = c_inc

# extract ASM include dirs
    dig_list = ['TargetArmAds', 'Aads', 'VariousControls', 'IncludePath']
    res, node = dig_in(dig_list, opt_node)
    if res == 1:
        a_inc = trim_XML_braces(ET.tostring(node)).replace(
            ",", " ").strip(whitespace)
        debug_print("parse_TARGET_OPTIONS() : a_inc = " + a_inc)
        retval['A_INC_DIRS'] = a_inc

    return retval

# parses target


def parse_TARGET(tnode):
    #                                  target name
    #                                        groups of files in the target
    #                                               options for the target
    Target = namedtuple('Target', 'tname tgroups toptions')
    tname = ""
    toptions = {}
    tgroups = list()
    for s in tnode:
        if s.tag == 'TargetName':
            tname = ET.tostring(s)
            tname = trim_XML_braces(tname)
            tname = tname.replace(" ", "_")
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

# checks IncludeInBuild key in properties


def check_IncludeInBuild(prop):
    inc_key = prop.get('IncludeInBuild')
    retval = 1
    if inc_key:
        if inc_key != '1':
            retval = 0
    return retval

# get custom text key in properties


def get_custom_text(prop, key):
    text = prop.get(key)
    retval = ""
    if text:
        if not text.startswith("\n"):
            retval = text
    return retval


# create output file
def check_outfile(n):
    output_file = Path(n)
    if output_file.is_file():
        print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL + "The file " +
              Style.BRIGHT + n + Style.RESET_ALL + " already exists! Overwrite the existing file (y/n)?")
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
            # does this file have custom includes?
            ip = get_custom_text(f.fopt, 'IncludePath')
            if ip != "":
                print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL + "The file " +
                      Style.BRIGHT + f.fpath + Style.RESET_ALL + " has custom include path!")
                writeln(ofile, "\n# >>>> custom include!\t\t" + ip)

            define = get_custom_text(f.fopt, 'Define')
            if define != "":
                print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL +
                      "The file " + Style.BRIGHT + f.fpath + Style.RESET_ALL + " has custom defines!")
                writeln(ofile, "\n# >>>> custom defines!\t\t" + define)

            undefine = get_custom_text(f.fopt, 'Undefine')
            if undefine != "":
                print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL + "The file " +
                      Style.BRIGHT + f.fpath + Style.RESET_ALL + " has custom undefines!")
                writeln(ofile, "\n# >>>> custom undefines!\t\t" + undefine)

            comm = ""
            if (int(f.ftype) != 1) and (int(f.ftype) != 7):
                comm = "#"
            if check_IncludeInBuild(f.fopt) != 1:
                comm = "#"
            beau = os.path.normpath(f.fpath)
            beau = beau.replace("\\", "/")
            if beau.startswith("../"):
                beau = beau[3:]
            writeln(ofile, comm + "\t\t" + beau)
        writeln(ofile, "\t)\n")

# writes LIST_OF_SOURCES variable


def write_LIST_OF_SOURCES(ofile, groups):
    writeln(ofile, "set\t(" + "${" + exec_name + "}" + "_LIST_OF_SOURCES")
    for g in groups:

        # does not work!
        define = get_custom_text(g.gopt, 'Define')
        if define != "":
            print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL +
                  "The group " + Style.BRIGHT + g.gname + Style.RESET_ALL + " has custom defines!")
            writeln(ofile, "\n# >>>> custom defines!\t\t" + define)

        undefine = get_custom_text(g.gopt, 'Undefine')
        if undefine != "":
            print(Fore.YELLOW + Style.BRIGHT + "\nWarning! " + Style.RESET_ALL + "The group " +
                  Style.BRIGHT + g.gname + Style.RESET_ALL + " has custom undefines!")
            writeln(ofile, "\n# >>>> custom undefines!\t\t" + undefine)
# ^^^^^^^^^^^^^^^

        comm = ""
        if check_IncludeInBuild(g.gopt) != 1:
            comm = "#"
        writeln(ofile, comm + "\t\t${GROUP_SRC_" + g.gname + "}")
    writeln(ofile, "\t)\n")

    writeln(ofile, "target_sources(" + "${" + exec_name + "}" +
            " PRIVATE ${${" + exec_name + "}" + "_LIST_OF_SOURCES} ${STARTUP_CODE_SOURCE})\n")


#
def write_defs(ofile, dic):
    s_out = "set(MCU " + dic['MCU'] + ")"
    writeln(ofile, s_out)
#    debug_print(s_out)
# c defs
    s_out = "target_compile_definitions(" + "${" + exec_name + "}" + \
        " PRIVATE " + dic['TARGET_C_DEFINES'] + ")"
    writeln(ofile, s_out)

# asm defs
    if len(dic['TARGET_ASM_DEFINES']) > 0:
        s_out = "target_compile_definitions(" + "${" + exec_name + "}" + \
            " PRIVATE " + dic['TARGET_ASM_DEFINES'] + ")"
        writeln(ofile, s_out)
    else:
        writeln(ofile, "\n")

# c undefs
# is there any of them?
    c_undef = dic['TARGET_C_UNDEFINES']
    if len(c_undef) > 0:

        #print("len(c_undefs) = " +str(len(c_undef)) + "\n")

        c_undef = " " + c_undef
        c_undef = c_undef.replace(" ", " -U")
        s_out = "target_compile_options(" + \
            "${" + exec_name + "}" + " PRIVATE " + c_undef + ")"
        writeln(ofile, s_out)

# asm undefs
    a_undef = dic['TARGET_ASM_UNDEFINES']
    if len(a_undef) > 0:

        #print("len(a_undefs) = " +str(len(a_undef)) + "\n")

        a_undef = " " + a_undef
        a_undef = a_undef.replace(" ", " -U")
        s_out = "target_compile_options(" + \
            "${" + exec_name + "}" + " PRIVATE " + a_undef + ")"
        writeln(ofile, s_out)

    return

# writes target include directories


def write_incs(ofile, in_string):
    splitted = in_string.split(";")
    for s in splitted:
        s1 = s.strip(whitespace)
        s2 = os.path.normpath(s1)
        s2 = s1.replace("\\\\", "/")
        if s2.startswith("../"):
            s2 = s2[3:]
        if not s2.startswith("\\n "):
            s_out = "target_include_directories(" + "${" + exec_name + "}" + \
                " PRIVATE " + s2 + ")"
            writeln(ofile, s_out)
            debug_print(s_out)
    s_out = "target_include_directories(" + \
        "${" + exec_name + "}" + " PRIVATE .)"
    writeln(ofile, s_out)
    writeln(ofile, "")
    return

# writes TARGET_NAME variable


def write_target_name(ofile, tname):
    s_out = "\n## ------- TARGET STARTS HERE -------"
    writeln(ofile, s_out)

    s_out = "set(TARGET_NAME " + tname + ")"
    writeln(ofile, s_out)
    


def write_add_exec(ofile, tname, mcu):
    exec_name_var = tname + "_" + mcu

    s_out = "set(" + exec_name + " " + exec_name_var + ")"
    writeln(ofile, s_out)
    s_out = "set(TARGET_NAME ${EXEC_NAME} )"
    writeln(ofile, s_out)

    s_out = "add_executable(${" + exec_name + "})\n"
    writeln(ofile, s_out)


def write_compile_options(ofile, opt):
    s_out = "target_compile_options(${" + exec_name + "}" + \
        " PRIVATE " + "${COMPILE_FLAGS} " + str(opt) + ")"
    writeln(ofile, s_out)


def write_link_options(ofile, opt):
    s_out = "\ntarget_link_options(\n\t\t\t\t${" + exec_name + "}" + " BEFORE PRIVATE \n" +\
        "\t\t\t\t\"-Wl,-Map=${" + exec_name + "}.map\"\n" +\
        "\t\t\t\t\"-Wl,-T${LDSCRIPT}\"\n" + \
        "\t\t\t\t\"-Wl,--gc-sections\"\n" + \
        "\t\t\t\t\"-Wl,--verbose\"\n" + \
        "\t\t\t\t\"-Wl,-V\"\n" + \
        "\t\t\t\t\"-Wl,--cref\"\n" +\
        "\t\t\t\t${COMPILE_FLAGS})\n"
    writeln(ofile, s_out)


def write_link_lib(ofile, opt):
    s_out = "\ntarget_link_libraries(\n\t\t\t\t${" + exec_name + "}\n" + \
        "\t\t\t\tc		# c runtime\n" + \
        "\t\t\t\tm		# math\n" + \
        "\t\t\t\tnosys	# for non-os\n" + \
        "\t\t\t\t)\n"
    writeln(ofile, s_out)


def add_custom_targets(ofile):
    s_out = "STM32_ADD_HEX_BIN_TARGETS(${" + exec_name + "})"
    writeln(ofile, s_out)
    s_out = "STM32_PRINT_SIZE_OF_TARGETS(${" + exec_name + "})"
    writeln(ofile, s_out)


def detect_mcu(in_mcu):
    mcu_dep = namedtuple('MCU_OPT', 'mcu_family mcu_comp_opt')
    mcu_dep1 = mcu_dep(
        "STM32F1", "-mcpu=cortex-m3 -mthumb -mfloat-abi=soft  -mno-thumb-interwork -v")
    mcu_dep3 = mcu_dep(
        "STM32F3", "-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16  -mno-thumb-interwork -v")
    mcu_dep4 = mcu_dep(
        "STM32F4", "-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16  -mno-thumb-interwork -v")

    mcus = (mcu_dep1, mcu_dep3, mcu_dep4)
    retval = ""

    for mcu in mcus:
        if in_mcu.startswith(mcu.mcu_family):
            retval = mcu.mcu_comp_opt
    return retval


def write_comp_flags(ofile, t):
    s_out = "set(COMPILE_FLAGS " + t + ")"
    writeln(ofile, s_out)


def detect_asm_src_and_ld(in_mcu):
    startup_code = namedtuple('ASM_SRC', 'mcu asm_file ld')

    startup1 = startup_code(
        "STM32F405RGTx", "startup_stm32f405xx.s", "STM32F405RGTx_FLASH.ld")
    startup2 = startup_code(
        "STM32F103CB", "startup_stm32f103xb.s", "STM32F103C8Tx_FLASH.ld")
    startup3 = startup_code(
        "STM32F303CB", "startup_stm32f303xc.s", "STM32F303CCTx_FLASH.ld")

    startups = (startup1, startup2, startup3)

    retval = "add_your_asm_file", "add_your_ld_script"

    for startup in startups:
        if in_mcu == startup.mcu:
            retval = startup.asm_file, startup.ld
    return retval


def write_startup_code_source(ofile, in_mcu):
    s_out = """
# The path to the asm startup file(s)
set(STARTUP_CODE_DIR ${CMAKE_CURRENT_SOURCE_DIR})

# A debug output
message("STARTUP_CODE_DIR = " ${STARTUP_CODE_DIR})

# The path to the linker script(s)
set(LINKER_SCRIPTS_DIR ${CMAKE_CURRENT_SOURCE_DIR})
message("LINKER_SCRIPTS_DIR = " ${LINKER_SCRIPTS_DIR})
"""
    writeln(ofile, s_out)
    asm, ld = detect_asm_src_and_ld(in_mcu)
    s_out = "set(STARTUP_CODE_SOURCE ${STARTUP_CODE_DIR}/%asmfile%)"
    s_out = s_out.replace("%asmfile%", asm)
    writeln(ofile, s_out)

    s_out = "set(LDSCRIPT ${STARTUP_CODE_DIR}/%ldfile%)"
    s_out = s_out.replace("%ldfile%", ld)
    writeln(ofile, s_out)


def main():

    # check python version
    if sys.version_info[0] == 3:
        py3 = 1
        print("python 3 detected!\n")
# check arguments
    if len(sys.argv) < 3:
        usage()
        exit(-1)

    keil_proj_file_n = sys.argv[1]
    debug_print(keil_proj_file_n)
    keil_proj_file = Path(keil_proj_file_n)

    if check_file_exists(keil_proj_file) == 0:
        print(Fore.RED + Style.BRIGHT + "Error!" + Style.RESET_ALL +
              " Can't find Keil project file " + Style.BRIGHT + str(keil_proj_file) + Style.RESET_ALL)
        exit(-2)

# check is file .uvprojx or not
    spl = os.path.splitext(str(keil_proj_file))
    debug_print(spl)
    if spl[1] != ".uvprojx":
        print("Error! Can't find Keil project file " + spl[0] + ".uvprojx")
        exit(-3)

    cmake_dir_n = sys.argv[2]
    debug_print("cmake_dir_n = " + cmake_dir_n)

    cmake_dir = Path(cmake_dir_n)
    if check_dir_exists(cmake_dir) == 0:
        print("Error! Can't find target directory " + str(cmake_dir))
        exit(-4)

    debug_print("cmake_dir_n = " + str(cmake_dir))
    tree = ET.parse(str(keil_proj_file))
    root = tree.getroot()
    for child in root:
        if child.tag == 'Targets':
            for child2 in child:
                if child2.tag == 'Target':
                    a = parse_TARGET(child2)
# generate cmake list for the target
                    ofile_raw = cmake_dir.joinpath(a.tname + "_" + out_file_name)
#                    cmake_dir_n + "\\" + a.tname + "_" + out_file_name
                    ofile_raw = os.path.realpath(ofile_raw)
                    ofile = check_outfile(ofile_raw)
# open and reset output file
                    text_file = open(str(ofile), "w+")
# write target name
                    write_target_name(text_file, a.tname)
# add_executable
                    write_add_exec(text_file, a.tname, a.toptions['MCU'])
# write defines for the target, and undefines
                    write_defs(text_file, a.toptions)
# wrile include directories
                    write_incs(text_file, a.toptions['C_INC_DIRS'])
                    write_incs(text_file, a.toptions['A_INC_DIRS'])

# try to detect MCU family
                    comp_flags = detect_mcu(a.toptions['MCU'])
                    write_comp_flags(text_file, comp_flags)

                    write_startup_code_source(text_file, a.toptions['MCU'])

# write cmake lists of sources to the outfile
                    write_lists(text_file, a.tgroups)
                    write_LIST_OF_SOURCES(text_file, a.tgroups)

                    write_compile_options(text_file, "")

                    write_link_options(text_file, "")
                    write_link_lib(text_file, "")
                    add_custom_targets(text_file)
                    text_file.close()
                    print(Fore.GREEN + Style.BRIGHT + "Success!" + Style.RESET_ALL +
                          " File " + Style.BRIGHT + str(ofile) + Style.RESET_ALL + " created.")


###############################################################################
if __name__ == "__main__":
    sys.argv = ["keil2cmake.py", "/home/tvv/work2/gcov_proof/MDK-ARM/./gcov_proof.uvprojx", "/home/tvv/playground"]
    init()
    main()

########################## E. O. F. ###########################################
