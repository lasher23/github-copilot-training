# 🚀 FastAPI Productivity Reporting System

This project is designed for **GitHub Copilot training purposes**. It is based on a simple FastAPI application and includes a series of training tasks to help developers learn how to effectively use GitHub Copilot for accelerating development, improving code quality, and integrating AI into their workflows.

---

## 📋 Features

- **Task Management**: Add, retrieve, and manage developer tasks.
- **Productivity Reports**: Generate reports with key metrics such as total tasks, completed tasks, and time spent.
- **MongoDB Integration**: Persistent data storage with MongoDB for tasks and users.
- **Asynchronous API**: Built with modern Python standards for high performance.
- **Swagger UI**: Interactive API documentation available at `/docs`.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Dependency Manager**: `uv` (configured via `pyproject.toml`)
- **Data Models**: Pydantic for validation and serialization

---

## 🎯 Training Purpose

This project is part of the **GitHub Copilot Training Program**. It includes six modules that guide developers through various aspects of using Copilot effectively:

1. **Module I — Context & Control**: Precise Prompting and Workspace Awareness
2. **Module II — Dynamic Interaction Modes**: Completions, Inline Chat, Chat Panel, Terminal
3. **Module III — Version Control & Quality**: Git Workflow Integration
4. **Module IV — Testing Framework**: Automating Tests and Policy Checks
5. **Module V — Agentic Workflows**: Delegating and Supervising Autonomous Agents
6. **Module VI — Vibe Coding**: The Integrated Exploration Challenge

Each module includes hands-on exercises to help you master specific Copilot features and workflows.

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** installed on your system.
2. **`uv` Package Manager**: Install `uv` for managing dependencies. [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
3. **MongoDB**: Install MongoDB locally or use Docker. [MongoDB Installation](https://www.mongodb.com/docs/manual/installation/)

### MongoDB Setup

You can run MongoDB using Docker:

```bash
docker run -d --name mongodb -p 27017:27017 mongo:7
```

Or install MongoDB locally and start the service.

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your MongoDB connection string if different from the default:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=productivity_app
   ```

### Installation & Running

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Start the application:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

### Running Tests

The test suite automatically manages MongoDB containers:

**Automatic Container Management**: Tests automatically start and stop a MongoDB Docker container. No manual setup required!

```bash
uv run pytest -v
```

**Using External MongoDB** (optional): If you prefer to use an external MongoDB instance:

```bash
export TEST_MONGODB_URL=mongodb://localhost:27017
uv run pytest -v
```

Run tests with coverage:

```bash
uv run pytest --cov=app tests/
```

**Note**: The automatic container management requires Docker to be installed and running. When Docker is unavailable and `TEST_MONGODB_URL` is not set, tests will skip.

---

## 🛡️ Developer Responsibility

This project uses GitHub Copilot to accelerate development. However, **developers are responsible for reviewing, testing, and validating all generated code** to ensure correctness, security, and compliance with project standards.

---

## 🙌 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [uv Package Manager](https://docs.astral.sh/uv/getting-started/installation/)

