#!/usr/bin/python2

import os
import argparse
import subprocess
import string
import sys
import math
import shutil

zephir_version = "master"
jsonc_version = "master"
zephir_installation_dir = '/usr/local/src/zephir'
global_cache_dir = '/var/cache/zmm/modules'
known_modules = {
	"shell": "https://github.com/wapmorgan/php-shell.git",
	"elastica": "https://github.com/ariskemper/celastica.git",
	"lynx": "https://github.com/lynx/lynx.git",
	"hoard-utils": "https://github.com/marcqualie/hoard-utils.git",
	"nano": "https://github.com/3axap4eHko/Nano.git",
	"epic": "https://github.com/aaroncox/zephir-epic.git",
	"nirlah": "https://github.com/Nirlah/Toolbelt.git",
	"cake": "https://github.com/jrbasso/cakephp-ext.git"
}

_suffixes = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB']

def file_size(size):
    # determine binary order in steps of size 10 
    # (coerce to int, // still returns a float)
    order = int(math.log(size, 2) / 10)
    # format file size
    # (.4g results in rounded numbers for exact matches and max 3 decimals, 
    # should never resort to exponent values)
    return '{:.4g} {}'.format(size / (1 << (order * 10)), _suffixes[order])

def dirsize(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def createParser ():
	parser = argparse.ArgumentParser()
	parser.add_argument('module', help = 'name of zephir module to install')
	parser.add_argument('version', help = 'version of this module', nargs = '?', default = 'master')
	parser.add_argument('repo', help = 'repo for this module', nargs = '?')
	parser.add_argument('-z', '--reinstall_zephir', action = 'store_true', help = 'forces zephir reinstallation')
	parser.add_argument('-l', '--local', action = 'store_true', help = 'store cache in current working dir')
	return parser

def installZephir ():
	cwd = os.getcwd()
	result = subprocess.call(['git', 'clone', 'https://github.com/phalcon/zephir.git', zephir_installation_dir])
	if result != 0:
		print "zephir installation failed"
		sys.exit(1);

	subprocess.call(['git', '-C', zephir_installation_dir, 'checkout', zephir_version])
	subprocess.call(['git', '-C', zephir_installation_dir, 'submodule', 'update', '--init'])
	os.chdir(os.path.join(zephir_installation_dir, 'json-c'))
	subprocess.call(['git', 'checkout', jsonc_version])

	result = subprocess.call(['sh', 'autogen.sh'])
	if result != 0:
		print "json-c (zephir dependency) installation failed"
		sys.exit(1)
	if subprocess.call('./configure') == 0 and subprocess.call('make') == 0 and subprocess.call(['make', 'install']) == 0:		
		print "json-c installed."
	else:
		print "errors occured during json-c installation"
		sys.exit(1)
	
	if subprocess.call([os.path.join(zephir_installation_dir, 'install'), '-c']) == 0:
		print "zephir compiled and installated."
	else:
		print "errors occured during zephir installation"
		sys.exit(1)
	os.chdir(cwd)
	

if __name__ == "__main__":
	parser = createParser()
	namespace = parser.parse_args();
	# check zephir installation
	if not os.path.isdir(zephir_installation_dir):
		installZephir()
	elif namespace.reinstall_zephir:
		shutil.rmtree(zephir_installation_dir)
		installZephir()

	# start cloning
	if namespace.local:
		dir = os.path.join(os.getcwd(), namespace.module)
	else:
		dir = os.path.join(global_cache_dir, namespace.module)
		if not os.path.isdir(global_cache_dir):
			os.makedirs(global_cache_dir)

	if string.find(namespace.module, '_') == 0:
		if namespace.module == '_cache':
			for file in os.listdir(global_cache_dir):
				print file + ' ' + file_size(dirsize(os.path.join(global_cache_dir, file)))
	else:
		if namespace.repo == None:
			if namespace.module in known_modules:
				namespace.repo = known_modules[namespace.module]
			else:
				print "this module has no known repo"
				sys.exit(1)

		if os.path.isdir(dir):
			print "updating ..."
			result = subprocess.call(['git', '-C', dir, 'pull', 'origin', 'master'])
		else:
			print "cloning ..."
			result = subprocess.call(['git', 'clone', namespace.repo, dir])

		if result != 0:
			print "failed"
			sys.exit(1)

		# version
		print "version is {}".format(namespace.version)
		subprocess.call(['git', '-C', dir, 'checkout', namespace.version])
		# start building
		os.chdir(dir)
		if subprocess.call(['zephir', 'build']) == 0:
			print "{} {} installation successful.".format(namespace.module, namespace.version)
		else:
			print "installation failed"
			sys.exit(1)

