

.PHONY: docker
docker:
	sudo apt update
	sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release
	curl -sSL https://get.docker.com | sh
	sudo usermod -aG docker ${USER}
	sudo systemctl enable docker
	@echo ==============================================
	@echo Re-launch your terminal, or run: newgrp docker
	@echo Ensure you re-activate your venv if necessary
	@echo ==============================================
