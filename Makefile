SHELL:=/bin/bash


init:
	sudo apt update
	sudo apt -y install i2c-tools python3-venv python3-smbus python3-testresources
	python3 -m venv --system-site-packages venv
	./venv/bin/python -m pip install pip setuptools setuptools-rust wheel --upgrade
	./venv/bin/python -m pip install -e .

docker-install:
	sudo apt update
	sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release apache2-utils
	curl -sSL https://get.docker.com | sudo sh
	sudo usermod -aG docker ${USER}
	sudo systemctl enable docker
	./venv/bin/python -m pip install docker-compose
	@echo =================================
	@echo = Please reboot your machine!!! =
	@echo =================================


fix-seccomp2:
	curl http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb --output libseccomp2_2.5.1-1_armhf.deb
	sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb
	rm libseccomp2_2.5.1-1_armhf.deb -f


clean:
	@echo WARNING - this will delete the Redis database
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]
	rm ./redis/data/appendonly.aof ./redis/data/dump.rdb -f


build:
	docker build -t erniesprojects/sepmon_rest -f Dockerfile.rest .
	docker build -t erniesprojects/sepmon_redis -f Dockerfile.redis .


.PHONY: init docker-install fix-seccomp2 clean build
