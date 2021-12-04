SHELL:=/bin/bash


.PHONY: init docker-install fix-seccomp2 mock clean build-rest build-redis push-rest push-redis

init:
	sudo apt update
	sudo apt -y install i2c-tools python3-venv python3-smbus python3-testresources python3-numpy python3-scipy
	python3 -m venv --system-site-packages venv
	./venv/bin/python -m pip install pip setuptools setuptools-rust wheel --upgrade --no-cache-dir
	./venv/bin/python -m pip install --no-cache-dir -e .

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
	sudo rm ./redis/data/appendonly.aof ./redis/data/dump.rdb -f
	sudo find septic_monitor -type f -name "*.pyc" -delete


build-rest:
	docker build -t erniesprojects/sepmon_rest -f Dockerfile.rest .

build-redis:
	docker build -t erniesprojects/sepmon_redis -f Dockerfile.redis .


push-rest:
	docker push erniesprojects/sepmon_rest

push-redis:
	docker push erniesprojects/sepmon_redis


mock:
	sudo apt -y install python3-numpy python3-scipy
	./venv/bin/python septic_monitor/mock.py



