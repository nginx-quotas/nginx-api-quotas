.PHONY: start watch down clean clean-cache unit-test functional-test test
.DEFAULT_GOAL := help

PYTHONPATH=$(PWD)/services/nginx-quota-limiter
export PYTHONPATH

UNIT_TEST_PATH=$(PYTHONPATH)/test/unit
export UNIT_TEST_PATH

FUNCTIONAL_TEST_PATH=$(PYTHONPATH)/test/functional
export FUNCTIONAL_TEST_PATH

INTEGRATION_TEST_PATH=$(PYTHONPATH)/test/integration
export INTEGRATION_TEST_PATH

start:
	docker-compose up -d

# quota on a single API gateway
start-01: 
	docker-compose -f ./examples/01-quota-w-nginx-kv-store-on-single-apigw/docker-compose.yml up -d

down-01:
	docker-compose -f ./examples/01-quota-w-nginx-kv-store-on-single-apigw/docker-compose.yml down

# quota on multiple API gateways
start-02: 
	docker-compose -f ./examples/02-quota-w-nginx-kv-store-on-multi-apigws/docker-compose.yml up -d

down-02:
	docker-compose -f ./examples/02-quota-w-nginx-kv-store-on-multi-apigws/docker-compose.yml down

ps:
	docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Names}}"

watch:
	watch 'docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Names}}"'

down:
	docker-compose down


clean: 
	docker kill $$(docker ps -q) 2> /dev/null || true
	docker system prune -a
	docker volume rm $(docker volume ls -qf dangling=true)

clean-cache:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type d -name .cache -exec rm -r {} \+
	find . -type d -name .pytest_cache -exec rm -r {} \+

lint:
	@flake8

unit-test:
	pytest $(UNIT_TEST_PATH)

functional-test:
	bash $(FUNCTIONAL_TEST_PATH)/run_test.sh

integration-test:
	bash $(INTEGRATION_TEST_PATH)/run_test.sh

test:
	pytest $(UNIT_TEST_PATH)
	bash $(FUNCTIONAL_TEST_PATH)/run_test.sh
	bash $(INTEGRATION_TEST_PATH)/run_test.sh
