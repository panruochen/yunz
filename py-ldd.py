#!/usr/bin/python

_____________________________ = '''

                     _     _     _    _              _____              _____                  _
                    | |   | |   | |  | |            |  __ \            |  __ \                | |
  _ __  _   _ ______| | __| | __| |  | |__  _   _   | |__) |_ _ _ __   | |__) |   _  ___   ___| |__   ___ _ __
 | '_ \| | | |______| |/ _` |/ _` |  | '_ \| | | |  |  ___/ _` | '_ \  |  _  / | | |/ _ \ / __| '_ \ / _ \ '_ \
 | |_) | |_| |      | | (_| | (_| |  | |_) | |_| |  | |  | (_| | | | |_| | \ \ |_| | (_) | (__| | | |  __/ | | |
 | .__/ \__, |      |_|\__,_|\__,_|  |_.__/ \__, |  |_|   \__,_|_| |_(_)_|  \_\__,_|\___/ \___|_| |_|\___|_| |_|
 | |     __/ |                               __/ |
 |_|    |___/                               |___/

'''

import sys, os, glob, stat
import shutil
import ConfigParser, optparse
import subprocess
from string import maketrans


def get_file_path(searchpaths, file) :
#    print(searchpaths, file)
    for path in searchpaths :
         for root, dirs, files in os.walk(path):
             for name in files :
                 if name.endswith(file) :
                     return os.path.join(root,name)
    return None

def get_dependencies(searchpaths, basefile, fileset) :
    global sys_readelf
    commands = [sys_readelf, '-d', basefile]
    proc = subprocess.Popen(commands, stdout=subprocess.PIPE)
    results = []

    out, err = proc.communicate()
    if proc.returncode != 0 :
        print >>sys.stderr, "Error on executing " + ' '.join(commands)
        exit(1)
    for line in out.split('\n') :
        a = line.split()
        if len(a) >= 4 and (a[2] == "Shared" and a[3] == "library:") :
            file = a[4][1:len(a[4])-1]
            if file not in fileset:
                filez = get_file_path(searchpaths, file)
                if filez is None :
                    print >> sys.stderr, "Can not locate file %s" % file
                    exit(1)
                filez = os.path.abspath(filez)
                results.append(filez)
#    print "%s :: got %u depends" % (basefile, len(results))
    return set(results)

def ldd(searchpaths, file) :
    basefile = os.path.abspath(file)
    results = set([basefile])
    set1    = set([basefile])
    while True :
        if len(set1) == 0 :
            break
        set2 = set([])
        for file in set1 :
            set3 = get_dependencies(searchpaths, file, results)
            for x in set3 :
                if x not in results :
                    results.add(x)
                    set2.add(x)
        set1 = set2
    results.remove(basefile)
    return results

def which(program) :
    if sys.platform == "win32":
        from distutils import spawn
        return spawn.find_executable(program)
    else :
        # print [ os.access(os.path.join(path, 'ntoarmv7-' + 'readelf'),os.X_OK) for path in os.environ["PATH"].split(os.pathsep)]
        # any(os.access(os.path.join(path, prefix + 'readelf'), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))
        pass

sys_readelf = None

# create the options parser
optionsparser = optparse.OptionParser()

# define the options we require/support
optionsparser.add_option("-c", "--config", help="use the specified config file", default='')
optionsparser.add_option("-p", "--prefix", help="specify the prefix for readelf utility", default='')
optionsparser.add_option("-s", "--searchpath", action='append', help="specify the search path for depended shared objects", default=[])

# parse the options
(options, args) = optionsparser.parse_args()

for prefix in [options.prefix, ''] :
    x = which(prefix + 'readelf')
    if x :
        sys_readelf = x
        break

if sys_readelf is None :
    print >>sys.stderr, "Can not find %sreadelf utility" % options.prefix
    exit(1)

searchpaths = options.searchpath
print searchpaths
print args
#exit(0)
for file in args :
    deps = ldd(searchpaths, file)
    print file
    for i in deps :
        print '  ', i
    print


