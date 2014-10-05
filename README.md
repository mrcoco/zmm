This is a manager for zephir modules.
> Zephir is a compiled high level language aimed to the creation of C-extensions for PHP

#### zmm
It handles process of zephir/json-c installation too, so do not do this manually.
You can select which version of module is needed and use another repo for known module or specify repo for unknown module.

#### Help
	usage: zmm.py [-h] [-v] {install,cache,clear,zephir} ...

	zmm - Zephir Modules Manager. It handles all work: installing zephir, cloning
	& compiling & installation module.

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit

	Actions:
	  {install,cache,clear,zephir}
	    cache               show global cache
	    clear               clears global cache

Examples:

1. clear global cache
> sudo ./zmm.py clear

2. show global cache
> ./zmm.py cache

#### Install
	usage: zmm.py install [-h] [-s {local,global}] module [version] [repo]

	install or update zephir module

	positional arguments:
	  module                name of zephir module to install
	  version               version of this module
	  repo                  repo for this module

	optional arguments:
	  -h, --help            show this help message and exit
	  -s {local,global}, --storage {local,global}
	                        change storage for this module's cache

Examples:

1. install *shell* module
> sudo ./zmm.py install shell

2. install *shell* module version *0.0.2*
> sudo ./zmm.py install shell 0.0.2

3. install *shell* module from other repo than cached in zmm version *0.0.4* (in this case version is required)
> sudo ./zmm.py install shell 0.0.4 git@github.com:forked/php-shell.git

#### Zephir
	usage: zmm.py zephir [-h] [-r] [-u] [-v VERSION] [-j VERSION]

	Reinstall or update zephir installation.

	optional arguments:
	  -h, --help            show this help message and exit
	  -r, --reinstall       force zephir reinstallation
	  -u, --update          runs zephir update process
	  -v VERSION, --version VERSION
	                        zephir version to install or update (if -u present)
	                        (default: master)
	  -j VERSION, --json_c_version VERSION
	                        json-c version to install or update (if -u present)
	                        (default: master)

Examples:

1. update to a specific version
> sudo ./zmm.py zephir -u -v 0.5.2

2. update zephir to a freshen version
> sudo ./zmm.py zephir -u -v master
