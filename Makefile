.PHONY: install build start dev test lint format clean docker-build docker-up docker-down all check

# Install dependencies
install:
	npm install

# Build the project
build:
	npm run build

# Start the production server
start:
	npm run start

# Start in development mode
dev:
	npm run dev

# Run tests
test:
	npm run test

# Run tests with coverage
test-coverage:
	npm run test:coverage

# Run linter
lint:
	npm run lint

# Fix lint issues
lint-fix:
	npm run lint:fix

# Check formatting
format-check:
	npm run format:check

# Format code
format:
	npm run format

# Type check
typecheck:
	npm run typecheck

# Run all checks (lint, format, typecheck, test)
check: lint format-check typecheck test

# Clean build artifacts
clean:
	npm run clean

# Build Docker image
docker-build:
	docker compose build

# Start Docker containers
docker-up:
	docker compose up -d

# Stop Docker containers
docker-down:
	docker compose down

# Full setup: install, check, and build
all: install check build
