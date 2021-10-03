SHELL:=/bin/bash

docker-install:
	sudo apt update
	sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release apache2-utils
	curl -sSL https://get.docker.com | sudo sh
	sudo usermod -aG docker ${USER}
	sudo systemctl enable docker
	./venv/bin/python -m pip install docker-compose
	@echo ==============================================
	@echo Re-launch your terminal, or run: newgrp docker
	@echo Ensure you re-activate your venv if necessary
	@echo ==============================================


fix:
	curl http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb --output libseccomp2_2.5.1-1_armhf.deb
	sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb	
	rm libseccomp2_2.5.1-1_armhf.deb -f

clean:
	@echo WARNING - this will delete the Redis database
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]
	rm ./redis/data/appendonly.aof ./redis/data/dump.rdb -f


.PHONY: clean docker-install fix
