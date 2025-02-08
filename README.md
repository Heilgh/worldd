# World Simulation Game

A simulation game where humans, animals, and plants interact in a dynamic world. Features intelligent entities with thoughts, behaviors, and complex interactions.

## Features

- Intelligent humans with thought processing and social interactions
- Animals with realistic behaviors (hunting, fleeing, resting)
- Plants with growth cycles and seasonal effects
- Dynamic weather and seasonal changes
- Complex entity interactions and relationships
- Beautiful modern graphics

## Installation

### Quick Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Run the development installation script:
```bash
python install_dev.py
```

### Manual Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Unix/MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Running the Game

Run the game using:
```bash
python -m src.main
```

## Controls

- WASD: Move camera
- +/-: Zoom in/out
- Left click: Select entity
- Space: Pause/Resume
- F3: Toggle debug info
- ESC: Exit game

## Requirements

- Python 3.8+
- Pygame 2.5.2
- Numpy 1.24.3
- Noise 1.2.2

## Development

The project uses modern Python packaging with `pyproject.toml`. To set up for development:

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Install in development mode:
```bash
pip install -e .
```

## Project Structure

```
src/
├── main.py              # Main entry point
├── constants.py         # Game constants and configuration
├── game.py             # Game loop and core logic
├── world/              # World generation and management
│   ├── generation/     # Terrain and world generation
│   ├── entities/       # Entity classes (humans, animals, plants)
│   └── systems/        # Game systems (weather, time, etc.)
└── ui/                 # User interface components
``` 