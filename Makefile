SHELL:=/bin/bash


.PHONY: init docker-install docker-config fix-seccomp2 mock clean build-base build-redis push-base push-redis

init:
	sudo apt update
	sudo apt -y install i2c-tools python3-venv python3-smbus python3-testresources python3-numpy python3-scipy postgresql-client-common postgresql-client-*
	python3 -m venv --clear --system-site-packages venv
	./venv/bin/python -m pip install pip setuptools setuptools-rust wheel --upgrade --no-cache-dir
	./venv/bin/python -m pip install --no-cache-dir -e .
	./venv/bin/python -m pip install --no-cache-dir ansible
	echo -e '\nsource .env' >> venv/bin/activate
	test -f .env || cp .env.sample .env

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


docker-config:
	sudo mkdir /etc/docker -p
	sudo cp daemon.json /etc/docker/daemon.json
	sudo systemctl restart docker


fix-seccomp2:
	curl http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb --output libseccomp2_2.5.1-1_armhf.deb
	sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb
	rm libseccomp2_2.5.1-1_armhf.deb -f


clean:
	@echo WARNING - this will delete database data
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]
	sudo find septic_monitor -type f -name "*.pyc" -delete
	./venv/bin/docker-compose down
	docker container prune -f
	docker volume rm septic_monitor_pgdata; echo pgdata deleted		
	sudo ./venv/bin/ansible-playbook ansible/fix-timescaledb-config.yml


build-base:
	docker build -t erniesprojects/sepmon_base -f Dockerfile.base .

build-redis:
	docker build -t erniesprojects/sepmon_redis -f Dockerfile.redis .


push-base:
	docker push erniesprojects/sepmon_base

push-redis:
	docker push erniesprojects/sepmon_redis


mock:
	sudo apt -y install python3-numpy python3-scipy
	./venv/bin/python septic_monitor/mock.py



