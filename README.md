This is a manager for zephir modules.
> Zephir is a compiled high level language aimed to the creation of C-extensions for PHP

#### zmm
It handles process of zephir/json-c installation too, so do not do this manually.
You can select which version of module is needed and use another repo for known module or specify repo for unknown module.

#### Help
	usage: zmm.py [-h] [-z] [-l] module [version] [repo]

	positional arguments:
	  module                name of zephir module to install
	  repo                  repo for this module
	  version               version of this module

	optional arguments:
	  -h, --help            show this help message and exit
	  -z, --reinstall_zephir
	                        forces zephir reinstallation
	   -l, --local           store cache in current working dir

#### Examples
1. install *shell* module
> sudo ./zmm.py shell

2. install *shell* module version *0.0.2*
> sudo ./zmm.py shell 0.0.2

3. install *shell* module from other repo than cached in zmm version *0.0.4* (in this case version is required)
> sudo ./zmm.py shell 0.0.4 git@github.com:forked/php-shell.git

4. list all cached modules
> ./zmm.py _cache

Additional functions:

1. reinstall zephir with json-c (edit versions in zmm.py header)
> sudo ./zmm.py _cache --reinstall_zephir

2. install module in local dir
> sudo ./zmm.py shell -l
