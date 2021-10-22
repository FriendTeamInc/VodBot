all:
	pip3 install .

build:
	python3 -m build

upload:
	python3 -m twine upload dist/*

clean:
	pip3 uninstall vodbot -y
	rm -rf VodBot.egg-info dist build