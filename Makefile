VENV ?= /tmp/tariffguard-venv
LAMBDA_BUILD ?= /tmp/tariffguard-lambda-build
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff

.PHONY: install test lint build-backend deploy destroy frontend-dev frontend-build seed

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e "backend[dev]"
	bash -lc 'source ~/.nvm/nvm.sh && cd frontend && npm install'

test:
	cd backend && $(PYTEST)

lint:
	cd backend && $(RUFF) check src tests

build-backend:
	rm -rf $(LAMBDA_BUILD) build/tariffguard-lambda.zip
	$(PYTHON) scripts/package_lambda.py --target $(LAMBDA_BUILD) --output build/tariffguard-lambda.zip

deploy:
	cd infra && terraform init && terraform apply

destroy:
	cd infra && terraform destroy

frontend-dev:
	bash -lc 'source ~/.nvm/nvm.sh && cd frontend && npm run dev'

frontend-build:
	bash -lc 'source ~/.nvm/nvm.sh && cd frontend && npm run build'

seed:
	$(PYTHON) scripts/seed.py --api-url "$$API_URL"
