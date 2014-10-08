install:
	cp zmm.py /usr/bin/zmm
	mkdir -p /var/cache/zmm/
uninstall:
	if [ -f /usr/bin/zmm ]; then rm /usr/bin/zmm; fi
	if [ -d /usr/local/src/zephir ]; then rm -Rf /usr/local/src/zephir; fi
