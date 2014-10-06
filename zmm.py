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

version = '1.2.0'
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

	install_parser = subparsers.add_parser('install', help = 'install zephir or zephir module')
	install_parser.add_argument('module', help = 'name of zephir module to install', nargs = '?')
	install_parser.add_argument('version', help = 'version of this module (default: master)', nargs = '?', default = 'master')
	install_parser.add_argument('repo', help = 'repo for this module', nargs = '?')	
	install_parser.add_argument('--zephir', action = 'store_true')
	install_parser.add_argument('--replace', action = 'store_true')

	update_parser = subparsers.add_parser('update', help = 'update zephir or zephir module')
	update_parser.add_argument('module', help = 'name of zephir module to update', nargs = '?')
	update_parser.add_argument('version', help = 'version of this module (default: master)', nargs = '?', default = 'master')
	update_parser.add_argument('--zephir', action = 'store_true')

	list_parser = subparsers.add_parser('list', help = 'show installed modules')
	remove_parser = subparsers.add_parser('remove', help = 'remove zephir or zephir module')
	remove_parser.add_argument('module', help = 'name of zephir module to remove', nargs = '?')
	remove_parser.add_argument('--zephir', action = 'store_true')

#	zephir_parser = subparsers.add_parser('zephir', description = 'Reinstall or update zephir installation.')
#	zephir_parser.add_argument('-r', '--reinstall', help = 'force zephir reinstallation', action = 'store_true')
#	zephir_parser.add_argument('-u', '--update', help = 'runs zephir update process', action = 'store_true')
#	zephir_parser.add_argument('-v', '--version', help = 'zephir version to install or update (if -u present) (default: ' + zephir_version + ')', metavar = 'VERSION', default = zephir_version)
#	zephir_parser.add_argument('-j', '--json_c_version', help = 'json-c version to install or update (if -u present) (default: ' + jsonc_version + ')', metavar = 'VERSION', default = jsonc_version)
	
	return parser

def openConfig ():
	config = ConfigParser.RawConfigParser()
	if os.path.isfile(os.path.join(global_cache_dir, 'db.cfg')):
		config.read(os.path.join(global_cache_dir, 'db.cfg'))
	return config

def saveConfig (config):
	with open(os.path.join(global_cache_dir, 'db.cfg'), 'wb') as configfile:
		config.write(configfile)
	

def checkModule (namespace):
	"""
	Checks that module exists in precached modules list.
	Checks that module is not already installed.
	"""
	if namespace.repo == None:
		if namespace.module in known_modules:
			namespace.repo = known_modules[namespace.module]
	else:
		print "this module has no known repo"
		sys.exit(1)

	if os.path.isdir(os.path.join(global_cache_dir, namespace.module)):
		# the same repo - propose update
		out, err = subprocess.Popen(['git', '-C', os.path.join(global_cache_dir, namespace.module), 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE).communicate()
		if out.strip() == namespace.repo:
			print "this module already installed. You should use _update_ command."
			sys.exit(1)
		# another repo - propose using --replace flag
		else:
			print "you trying install another module with this name. Try using --replace flag to replace it with new module".format(namespace.module)
			sys.exit(1)

def _updateDb (namespace):
	# store version and repo in db
	config = openConfig()
	if config.has_section(namespace.module):
		config.remove_section(namespace.module)

	config.add_section(namespace.module)
	config.set(namespace.module, 'version', namespace.version)
	config.set(namespace.module, 'repo', namespace.repo)
	saveConfig(config)


def installModule (namespace):
	checkModule(namespace)
	dir = os.path.join(global_cache_dir, namespace.module)
	# delete module if flag --replace passed
	if os.path.isdir(dir) and namespace.replace:
		shutil.rmtree(dir)
	_updateDb(namespace)

	if subprocess.call(['git', 'clone', namespace.repo, dir]) != 0:
		print "Could not clone repo"
		sys.exit(1)

	if subprocess.call(['git', '-C', dir, 'checkout', namespace.version]) != 0:
		print "Could not select this version: {}".format(namespace.version)
		sys.exit(1)

	if os.chdir(dir) == None and subprocess.call(['zephir', 'build']) == 0:
		print "Sucessfully installed"
		print namespace.module + ' ' + namespace.version
		sys.exit(0)

def updateModule (namespace):
	dir = os.path.join(global_cache_dir, namespace.module)
	if not os.path.isdir(dir):
		print "Can not update a non-installed module. Try using install command."
		sys.exit(1)
	os.chdir(dir)
	if subprocess.call(['git', 'pull', 'origin', 'master']) != 0:
		print "Could not updat repo"
		sys.exit(1)

	config = openConfig()
	config.set(namespace.module, 'version', namespace.version)
	saveConfig(config)

	if subprocess.call(['git', 'checkout', namespace.version]) != 0:
		print "Could not select this version: {}".format(namespace.version)
		sys.exit(1)

	if subprocess.call(['zephir', 'build']) == 0:
		print "updated ({})".format(namespace.version)
		sys.exit(0)

def removeModule (namespace):
	dir = os.path.join(global_cache_dir, namespace.module)
	if os.path.isdir(dir):
		shutil.rmtree(dir)
	config = openConfig()
	if config.has_section(namespace.module):
		config.remove_section(namespace.module)
	saveConfig(config)

def installZephir (zephir_version):
	cwd = os.getcwd()
	print "connecting with https://github.com/phalcon/zephir.git"
	if not os.path.isdir(zephir_installation_dir):
		result = subprocess.call(['git', 'clone', '--quiet', 'https://github.com/phalcon/zephir.git', zephir_installation_dir])
	else:
		os.chdir(zephir_installation_dir)
		result = subprocess.call(['git', 'pull', '--quiet', 'origin', 'master'])
	if result != 0:
		print "zephir installation failed"
		sys.exit(1);
	os.chdir(zephir_installation_dir)
	if subprocess.call(['git', 'checkout', zephir_version]) != 0:
		print "Could not fetch {} version of zephir".format(zephir_version)
		sys.exit(1)
	subprocess.call(['git', 'submodule', '--quiet', 'update', '--init'])
	_compileZephir()
	sys.exit(0)

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
		if namespace.zephir:
			installZephir(namespace.module if namespace.module != None else namespace.version) # some hack for actual version value
		elif namespace.module != None:
			installModule(namespace)
		else:
			print "You should add module name or --zephir flag"
			sys.exit(1)
	elif namespace.command == 'update':
		if namespace.zephir:
			installZephir(namespace.module if namespace.module != None else namespace.version) # some hack for actual version value
		elif namespace.module != None:
			updateModule(namespace)
		else:
			print "You should add module name or --zephir flag"
			sys.exit(1)
	elif namespace.command == 'remove':
		if namespace.zephir:
			if shutil.rmtree(zephir_installation_dir):
				print "Zephir deleted"
				sys.exit(0)
		else:
			removeModule(namespace)
			print "{} removed".format(namespace.module)
			sys.exit(0)
	elif namespace.command == 'list':
		config = openConfig()
		i = 0
		for section_name in config.sections():
			i+=1
			print "{}. {}".format(i, section_name)
			print "Repo: {}".format(config.get(section_name, 'repo'))
			print "Version: {}".format(config.get(section_name, 'version'))
