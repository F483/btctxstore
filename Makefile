# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


help:
	@echo "Some usefull development shortcuts."
	@echo "  clean      Remove all generated files."
	@echo "  test       Run tests and analisys tools."
	@echo "  devsetup   Setup development environment."
	@echo "  build      Build package."
	@echo "  publish    Upload package to pypi."


clean:
	@rm -rf env
	@rm -rf apigen.egg-info
	@rm -rf build
	@rm -rf dist
	@find | grep -i ".*\.pyc$$" | xargs -r -L1 rm


devsetup: clean
	@virtualenv -p /usr/bin/python2 env/py2
	@virtualenv -p /usr/bin/python3 env/py3
	@env/py2/bin/python setup.py develop
	@env/py3/bin/python setup.py develop


test:
	env/py2/bin/python setup.py test # test python 2
	env/py3/bin/python setup.py test # test python 3
	# TODO add static analisys
	# TODO add lint
	# TODO add coverage


publish: test
	env/py3/bin/python setup.py register sdist upload


# import pudb; pu.db # set break point
