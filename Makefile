all:

docker-compose-build:
	docker compose -f src/docker-compose.yml build
.PHONY: docker-image

docker-compose-up: docker-compose-build
	docker compose -f src/docker-compose.yml up -d
.PHONY: docker-compose-up

docker-compose-up-nobuild:
	docker compose -f src/docker-compose.yml up -d

docker-compose-down:
	docker compose -f src/docker-compose.yml stop -t 10
	docker compose -f src/docker-compose.yml down --remove-orphans
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f src/docker-compose.yml logs -f
.PHONY: docker-compose-logs
