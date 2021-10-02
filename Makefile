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
	#sudo cp /var/lib/dpkg/diversions /var/lib/dpkg/diversions.bak
	sudo mv /var/lib/dpkg/diversions /var/lib/dpkg/diversions.old.bak
	sudo apt-get -f install
	sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release apache2-utils
	

clean:
	@echo WARNING - this will delete the Redis database
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]
	rm ./redis/data/appendonly.aof ./redis/data/dump.rdb -f


.PHONY: clean docker-install fix
