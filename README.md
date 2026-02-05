# first-claude-project

A Node.js/TypeScript project with a complete development workflow.

## Tech Stack

- **Language:** TypeScript
- **Runtime:** Node.js
- **Testing:** Jest with ts-jest
- **Linting:** ESLint with TypeScript support
- **Formatting:** Prettier
- **CI/CD:** GitHub Actions
- **Containerization:** Docker with multi-stage builds

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Docker (optional, for containerized builds)

### Installation

```bash
npm install
```

### Development

```bash
# Run in development mode
npm run dev

# Build the project
npm run build

# Start the built project
npm run start
```

## Available Commands

| Command              | Description                          |
| -------------------- | ------------------------------------ |
| `npm run dev`        | Run in development mode with ts-node |
| `npm run build`      | Compile TypeScript to JavaScript     |
| `npm run start`      | Run the compiled application         |
| `npm run test`       | Run tests                            |
| `npm run test:watch` | Run tests in watch mode              |
| `npm run test:coverage` | Run tests with coverage report    |
| `npm run lint`       | Check for lint errors                |
| `npm run lint:fix`   | Auto-fix lint errors                 |
| `npm run format`     | Format code with Prettier            |
| `npm run format:check` | Check code formatting              |
| `npm run typecheck`  | Run TypeScript type checking         |
| `npm run clean`      | Remove build artifacts               |

A `Makefile` is also included for convenience:

```bash
make install       # Install dependencies
make check         # Run all checks (lint, format, typecheck, test)
make build         # Build the project
make all           # Install, check, and build
make docker-build  # Build Docker image
make docker-up     # Start containers
make docker-down   # Stop containers
```

## Project Structure

```
├── .github/workflows/ci.yml   # GitHub Actions CI pipeline
├── src/
│   ├── index.ts                # Application entry point
│   ├── utils.ts                # Utility functions
│   └── utils.test.ts           # Unit tests
├── .eslintrc.json              # ESLint configuration
├── .prettierrc                 # Prettier configuration
├── docker-compose.yml          # Docker Compose config
├── Dockerfile                  # Multi-stage Docker build
├── jest.config.ts              # Jest test configuration
├── Makefile                    # Make shortcuts
├── package.json                # Project dependencies and scripts
└── tsconfig.json               # TypeScript configuration
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and PR to `main`:

1. Installs dependencies
2. Checks code formatting
3. Runs the linter
4. Runs type checking
5. Runs tests with coverage
6. Builds the project

Tests run against Node.js 18 and 20.

## Docker

Build and run the project in a container:

```bash
# Build the image
docker compose build

# Run the container
docker compose up -d

# Stop the container
docker compose down
```

The Dockerfile uses a multi-stage build to keep the production image small.

## License

MIT
