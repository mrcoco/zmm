This is a manager for zephir modules.
> Zephir is a compiled high level language aimed to the creation of C-extensions for PHP

#### zmm
It handles process of zephir/json-c installation too, so do not do this manually.
You can select which version of module is needed and use another repo for known module or specify repo for unknown module.

#### Help
There's 4 basic actions:

1. **install**
2. **update**
3. **remove**
4. **list**

## Install usage:

> sudo python zmm.py install **module_name** [**module_version**] [**module_repo**]

Installs a module. Default versio: master.

> sudo python zmm.py install --zephir [**zephir_version**]

Installs Zephir. Default version: master.

## Update usage:

> sudo python zmm.py update **module_name** [**module_version**]

Updates a module. Default version: master.

> sudo python zmm.py update --zephir [**zephir_version**]

Updates Zephir. Default version: master.

## Remove usage:

> sudo python zmm.py remove **module_name**

Removes a module.

> sudo python zmm.py remove --zephir

Removes Zephir.
