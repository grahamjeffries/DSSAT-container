import os
import shutil
import logging
import datetime

from distutils.dir_util import copy_tree


logging.basicConfig(level=logging.INFO)

VERSION_MAJOR = 4
VERSION_MINOR = 6
VERSION = '%s%s' % (VERSION_MAJOR, VERSION_MINOR)
ROOT_DIR = os.path.abspath('.')
SOURCE_DIR = os.path.abspath(os.path.join('.', 'dssat-csm'))
EXE_DIR = os.path.join(ROOT_DIR, 'DSSAT%s' % VERSION)
EXE_PATH = os.path.join(EXE_DIR, 'DSCSM0%s.EXE' % VERSION)


def enable_linux_mode(filename):
    '''
    Enable linux mode by commenting windows flags and uncommenting linux flags
    '''
    logging.info("Enable linux mode: %s" % filename)
    file_path = os.path.join(SOURCE_DIR, filename)
    file_path_temp = file_path + "_tmp"

    out_file = open(file_path_temp, 'w')
    with open(file_path, 'r') as f:
        for line in f:
            # comment out windows flags
            if "!dos, windows" in line.lower():
                line = "!" + line[1:]
            # uncomment unix flags
            elif "!linux, unix" in line.lower():
                line = " " + line[1:]
            out_file.write(line)

    out_file.close()

    os.remove(file_path)
    os.rename(file_path_temp, file_path)


def create_makefile():
    '''
    Generate a makefile for compiling DSSAT. Original function by Kelly Thorp with modifications by Graham Jeffries
    '''
    logging.info("Creating makefile")

    compiler = 'gfortran'
    # fcflags = '-O2 -freal-loops -ffixed-line-length-132 ' + \
    #           '-ffree-line-length-huge -c'  # g95
    # includes = '-fmod=$(OD)/mod'  # g95
    fcflags = '-O2 -ffixed-line-length-132 -ffree-line-length-none ' + \
              '-fd-lines-as-comments -c'
    includes = '-I$(OD)/mod -J$(OD)/mod'

    obj_path = os.path.join(ROOT_DIR, 'obj')
    obj_dirs = ['mod', 'OP_OBS', 'ORYZA', 'SALUS', 'ttutil']

    if not os.path.exists(EXE_DIR):
        os.mkdir(EXE_DIR)

    if not os.path.exists(obj_path):
        os.mkdir(obj_path)

    for obj_dir in obj_dirs:
        if not os.path.exists(os.path.join(obj_path, obj_dir)):
            os.mkdir(os.path.join(obj_path, obj_dir))

    # Obtain Fortran source files
    src_files = []
    for dirpath, dirnames, files in os.walk(SOURCE_DIR):
        for filename in files:
            if '.f' in filename.lower():
                f = open(os.path.join(dirpath, filename), 'r')
                lines = f.readlines()
                f.close()
                for line in lines:
                    line = line.lower()
                    if 'end' in line or 'module' in line:
                        src_files.append(os.path.join(dirpath, filename))
                        logging.debug(filename)
                        break
    if len(src_files) == 0:
        logging.error("DSSAT source code files not found.")
        return

    # Sort Fortran source files to get compile order
    logging.debug('Sorting Fortran source files...')
    src_files_sorted = []
    req_mod = []
    inc_mod = []
    comp_mod = []
    finished = False

    while not finished:
        for src_file in src_files:
            if src_file in src_files_sorted:
                continue
            f = open(src_file, 'r')
            lines = f.readlines()
            f.close()
            req_mod[:] = []
            inc_mod[:] = []

            for line in lines:
                line1 = line.lower().strip()
                line2 = line.lower().strip()
                if 'use ' in line1[0:4]:
                    line1 = line1.split(' ')[1]
                    line1 = line1.split(',')[0]
                    line1 = line1.split(';')[0]
                    line1 = line1.split('\t')[0]
                    logging.debug(line1)
                    req_mod.append(line1)  # required modules
                if 'module ' in line2[0:7]:
                    line2 = line2.split(' ')[1]
                    line2 = line2.split(',')[0]
                    line2 = line2.split(';')[0]
                    line2 = line2.split('\t')[0]
                    logging.debug(line2)
                    inc_mod.append(line2)  # included modules

            modcount = 0
            for mod in req_mod:
                if mod in comp_mod or mod in inc_mod:
                    modcount += 1
                    continue

            if modcount == len(req_mod):
                src_files_sorted.append(src_file)
                for mod in req_mod:
                    comp_mod.append(mod)
                for mod in inc_mod:
                    comp_mod.append(mod)
                comp_mod = list(set(comp_mod))
                logging.debug(src_file)
                if len(src_files_sorted) == len(src_files):
                    finished = True

    # Write makefile
    logging.debug('Writing makefile...')
    with open(os.path.join(ROOT_DIR, 'makefile'), 'w') as f:
        f.write('#Makefile to compile DSSAT-CSM\n')
        f.write('#%s\n\n' % datetime.datetime.now()
                                             .strftime('%m/%d/%y %I:%M:%S %p'))
        f.write('FC = %s\n' % compiler)
        f.write('FCFLAGS = %s\n' % fcflags)
        f.write('SD = %s\n' % SOURCE_DIR)
        f.write('OD = %s\n' % obj_path)
        f.write('EXE = %s\n' % EXE_PATH)
        f.write('INCLUDE = %s\n\n' % includes)
        f.write('OBJS += \\\n')
        string = ''

        for i in src_files_sorted:
            basename = os.path.splitext(os.path.basename(i))[0]
            dirname = os.path.dirname(i)
            reldir = os.path.relpath(dirname, SOURCE_DIR)
            reldir1 = os.path.splitext(reldir)
            logging.debug(reldir1)
            if reldir1[0] == '.':
                relfile = '/' + basename
            else:
                relfile = '/%s/%s' % (reldir1[0], basename)
            string += '\t$(OD)%s.o \\\n' % relfile

        f.write(string[:-2] + '\n\n')
        f.write('all: $(EXE)\n\n')
        f.write('$(EXE): $(OBJS)\n')
        f.write("\t@echo 'Building target: $@'\n")
        f.write("\t@echo 'Invoking Fortran Linker'\n")
        f.write("\t$(FC) -o $(EXE) $(OBJS)\n")
        f.write("\t@echo 'Finished building target: $@'\n")
        f.write("\t@echo ' '\n\n")

        for ext in ['.for', '.f90', '.F90']:
            f.write('$(OD)/%.o: $(SD)/%' + ext + '\n')
            f.write("\t@echo 'Building file: $<'\n")
            f.write("\t@echo 'Invoking %s Compiler'\n" % compiler)
            f.write("\t$(FC) $(INCLUDE) $(FCFLAGS) $< -o $@\n")
            f.write("\t@echo 'Finished building: $<'\n")
            f.write("\t@echo ' '\n\n")

        f.write('clean:\n')
        f.write('\t-rm $(EXE) $(OBJS) $(OD)/mod/*.mod\n')
        f.write("\t@echo ' '\n\n")


def copy_data_files():
    '''
    Copy the DSSAT "Data" folder to the executable folder because it contains
    default parameter and variable values
    '''
    copy_tree(os.path.join(SOURCE_DIR, 'Data'), EXE_DIR)


def copy_dssatpro():
    '''
    Copy the DSSATPRO.Lxx file into the executable folder
    '''
    dssatpro = 'DSSATPRO.L%s' % VERSION
    shutil.copy2(os.path.join(ROOT_DIR, dssatpro),
                 os.path.join(EXE_DIR, dssatpro))


if __name__ == '__main__':
    enable_linux_mode('ModuleDefs.for')
    enable_linux_mode('CRSIMDEF.for')
    create_makefile()
    copy_data_files()
    copy_dssatpro()
    misc_renamings()
