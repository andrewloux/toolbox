.PHONY: install build start dev clean migrate

install:
	npm install
	npm run prisma:generate

build:
	npm run build

start: build
	npm start -- --url $(url)

clean:
	rm -rf dist
	rm -rf node_modules

# Combined commands
setup: clean install build

	migrate: npx prisma migrate deploy

# Example usage:
# make setup
# make start url="https://openai.com/careers/search/"
# make dev url="https://openai.com/careers/search/"
