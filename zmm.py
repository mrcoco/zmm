#!/usr/bin/env python2
import ConfigParser
import os
import argparse
import platform
import subprocess
import string
import sys
import math
import shutil

version = '1.1.0'
zephir_version = "master"
jsonc_version = "master"

if platform.system() == "Windows":
        zephir_installation_dir = "C:\zmm\zephir"
else:
    zephir_installation_dir = '/usr/local/src/zephir'

if platform.system() == "Windows":
    global_cache_dir = "C:\zmm\cache"
else:
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
    if size <= 0:
        return 'zero bytes'
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
	parser = argparse.ArgumentParser(
            description = '''zmm - Zephir Modules Manager. It handles all work: installing zephir, cloning & compiling & installation module.'''
            )
	parser.add_argument('-v', '--version', action = 'version', version = '%(prog)s {}'.format(version))
	subparsers = parser.add_subparsers(dest='command',
                title = 'Actions')

	install_parser = subparsers.add_parser('install', description = 'install or update zephir module')
	install_parser.add_argument('module', help = 'name of zephir module to install')
	install_parser.add_argument('version', help = 'version of this module', nargs = '?', default = 'master')
	install_parser.add_argument('repo', help = 'repo for this module', nargs = '?')	
	install_parser.add_argument('-s', '--storage', choices=['local', 'global'], help = "change storage for this module's cache", default = 'global')

	cache_parser = subparsers.add_parser('cache', help = 'show global cache')
	clear_parser = subparsers.add_parser('clear', help = 'clears global cache')

        zephir_parser = subparsers.add_parser('zephir', description = 'Reinstall or update zephir installation.')
        zephir_parser.add_argument('-r', '--reinstall', help = 'force zephir reinstallation', action = 'store_true')
	zephir_parser.add_argument('-u', '--update', help = 'runs zephir update process', action = 'store_true')
	zephir_parser.add_argument('-v', '--version', help = 'zephir version to install or update (if -u present) (default: ' + zephir_version + ')', metavar = 'VERSION', default = zephir_version)
	zephir_parser.add_argument('-j', '--json_c_version', help = 'json-c version to install or update (if -u present) (default: ' + jsonc_version + ')', metavar = 'VERSION', default = jsonc_version)
	
	return parser

def createConfig ():
	config = ConfigParser.RawConfigParser()
	if os.path.isfile(os.path.join(global_cache_dir, 'repos.cfg')):
		config.read(os.path.join(global_cache_dir, 'repos.cfg'))
		if not config.has_section('repos'):
			config.add_section('repos')
	else:
		config.add_section('repos')
	return config

def installModule (namespace):
	# install zephir
	if not os.path.isdir(zephir_installation_dir):
		installZephir(zephir_version, jsonc_version)

	# check cache dir
	if namespace.storage == 'local':
		dir = os.path.join(os.getcwd(), namespace.module)
	else:
		dir = os.path.join(global_cache_dir, namespace.module)
		if not os.path.isdir(global_cache_dir):
			os.makedirs(global_cache_dir)
	
	if namespace.repo == None:
		if namespace.module in known_modules:
			namespace.repo = known_modules[namespace.module]
	else:
		print "this module has no known repo"
		sys.exit(1)

	# check that repo different
	config = createConfig()
	if config.has_option('repos', namespace.module):
		if not (config.get('repos', namespace.module) == namespace.repo):
			if namespace.storage == 'global' and os.path.isdir(dir):
				shutil.rmtree(dir)

	if os.path.isdir(dir):
		print "updating ..."
		result = subprocess.call(['git', '-C', dir, 'pull', 'origin', 'master'])
	else:
		print "cloning ..."
		result = subprocess.call(['git', 'clone', namespace.repo, dir])

	if result != 0:
		print "failed"
		sys.exit(1)

	config.set('repos', namespace.module, namespace.repo)
	with open(os.path.join(global_cache_dir, 'repos.cfg'), 'wb') as configfile:
            config.write(configfile)

	# version
	print "version is {}".format(namespace.version)
	# save from hitting the leg
	if subprocess.call(['git', '-C', dir, 'checkout', namespace.version]) != 0:
		print "This version is not present in repo"
		sys.exit(1)
	# start building
	os.chdir(dir)
	if subprocess.call(['zephir', 'build']) == 0:
		print "{} {} installation successful.".format(namespace.module, namespace.version)
	else:
		print "installation failed"
		sys.exit(1)

def installZephir (zephir_version, jsonc_version):
	cwd = os.getcwd()
	result = subprocess.call(['git', 'clone', 'https://github.com/phalcon/zephir.git', zephir_installation_dir])
	if result != 0:
		print "zephir installation failed"
		sys.exit(1);
	os.chdir(zephir_installation_dir)
	subprocess.call(['git', 'checkout', zephir_version])
	subprocess.call(['git', 'submodule', 'update', '--init'])
	subprocess.call(['git', '-C', os.path.join(zephir_installation_dir, 'json-c'), 'checkout', jsonc_version])
	_compileZephir()
	os.chdir(cwd)

def updateZephir ():
	cwd = os.getcwd()
	os.chdir(zephir_installation_dir)
	if subprocess.call(['git', 'pull']) != 0:
		print "Error occured"
		sys.exit(1)
	if subprocess.call(['git', 'checkout', namespace.version]) != 0:
		print "This version in not present in the repo"
		sys.exit(1)
	subprocess.call(['git', 'submodule', 'update', '--init'])
	subprocess.call(['git', '-C', os.path.join(zephir_installation_dir, 'json-c'), 'checkout', namespace.json_c_version])
	_compileZephir()
	os.chdir(cwd)
	

def _compileZephir ():
	"""
	Compiles zephir in current folder
	"""
	os.chdir(os.path.join(os.getcwd(), 'json-c'))
	result = subprocess.call(['sh', 'autogen.sh'])
	if result != 0:
		print "json-c (zephir dependency) installation failed"
		sys.exit(1)
	if subprocess.call('./configure') == 0 and subprocess.call('make') == 0 and subprocess.call(['make', 'install']) == 0:		
		print "json-c installed."
	else:
		print "errors occured during json-c installation"
		sys.exit(1)
	
	if os.chdir(os.path.dirname(os.getcwd())) == None and subprocess.call(['./install', '-c']) == 0:
		print "zephir compiled and installated."
	else:
		print "errors occured during zephir installation"
		sys.exit(1)

def listCache ():
    for file in os.listdir(global_cache_dir):
        if os.path.isdir(os.path.join(global_cache_dir, file)):
            print file + ' ' + file_size(dirsize(os.path.join(global_cache_dir, file)))

def clearCache ():
    for file in os.listdir(global_cache_dir):
        if os.path.isdir(os.path.join(global_cache_dir, file)):
            shutil.rmtree(os.path.join(global_cache_dir, file))

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

if __name__ == "__main__":
	parser = createParser()
	namespace = parser.parse_args();

        if namespace.command == 'install':
		installModule(namespace)
        elif namespace.command == 'zephir':
		# check zephir installation
		if not os.path.isdir(zephir_installation_dir):
			print "zephir is not installed"
			print "run installation of any module to install it"
			sys.exit(1)
		elif namespace.reinstall:
			print "reinstalling previous version..."
			shutil.rmtree(zephir_installation_dir, onerror = onerror)
			installZephir(namespace.version, namespace.json_c_version)
		elif namespace.update:
			print "updating zephir ..."
			updateZephir(namespace.version, namespace.json_c_version)
		else:
			print "Zephir already installed (try using --reinstall or --update options)"
			sys.exit(0)
	elif namespace.command == 'cache':
		listCache()
	elif namespace.command == 'clear':
		clearCache()
        else:
		print "Choice command"
		sys.exit(1)
