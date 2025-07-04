# DjiKMZ - DJI Task Plan KMZ File Generator

A Python package for generating DJI task plan KMZ files with comprehensive type safety, validation, and integrity checks.

## Goal

- 🛡️ **Type Safety**: Full type hints and Pydantic models for all data structures
- ✅ **Validation**: Comprehensive validation of waypoints, coordinates, and flight parameters
- 🔒 **Integrity Checks**: Built-in validation for DJI-specific constraints and limits
- 📦 **KMZ Generation**: Generate valid KMZ files compatible with DJI flight planning software
- 🎯 **Abstraction**: High-level API for easy waypoint and mission creation
- 🧪 **Well Tested**: Comprehensive test suite with high coverage

## Installation

```bash
pip install djikmz
```

## Quick Start


## API Reference

### Validation 

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/djikmz.git
cd djikmz

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
isort src/ tests/
```
