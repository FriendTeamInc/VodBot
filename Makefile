all:
	pip3 install .

clean:
	pip3 uninstall vodbot -y
	rm -rf VodBot.egg-info dist build