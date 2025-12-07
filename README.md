# minemind

**A custom Python package that launches an interactive Read-Eval-Print Loop (REPL) environment.**

## Overview

The `minemind` package provides a custom command-line interface (CLI) that allows users to interact with the core application logic (board generation, solving, state management, etc.) found within the `minemind/core` module.

The application is launched via the `minemind` command, which starts a persistent shell environment for executing game or solver actions.

-----

## Installation

### Prerequisites

  * Python **3.8 or higher** is required.

### Local Installation (Developer Mode)

1. Navigate to the project root:
    ```bash
    cd /path/to/minemind
    ```

2. Install in editable mode:
    ```bash
    pip install -e .
    ```

-----

## Usage

Launch the application:

```bash
minemind
```

You will see:

```
Welcome to the minemind shell. Type help or ? to list commands.
(minemind)
```

### Shell Commands (from `cli.py`)

| Command | Description |
|--------|-------------|
| `help` or `?` | Show available commands |
| `exit` / `quit` | Exit the shell |
| `new`, `solve`, `flag`, `render` | Example custom commands |

-----

## Running Tests

From the project root:

```bash
python -m unittest discover -s minemind\tests -p "test_*.py"
```

-----

## Project Structure

```
minemind/
├── minemind/
│   ├── __main__.py
│   ├── cli.py
│   ├── render.py
│   └── core/
│       ├── board.py
│       ├── solver.py
│       └── ...
├── pyproject.toml
└── tests/
```