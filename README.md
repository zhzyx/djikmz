# DjiKMZ - DJI Task Plan KMZ File Generator

> **⚠️ DEVELOPMENT STATUS NOTICE**
> 
> This project is currently in **active development and testing phase**. Due to time and resource constraints, real-world flight testing has only covered partial functionality and drone models. (Mostly M350)
> 
> **Please use with caution in production environments.** We strongly recommend thorough testing/validation on controller before field deployment.
> 
> 🤝 **Contributions and bug reports are welcome!** Help us improve the library by:
> - Testing with different drone models
> - Reporting issues and edge cases  
> - Contributing code improvements
> - Sharing real-world usage experiences

A Python package for generating DJI task plan KMZ files with comprehensive type safety, validation, and integrity checks.

## Goal

- 🛡️ **Type Safety**: Full type hints and Pydantic models for all data structures
- ✅ **Validation**: Comprehensive validation of waypoints, coordinates, and flight parameters
- 🔒 **Integrity Checks**: Built-in validation for DJI-specific constraints and limits
- 📦 **KMZ Generation**: Generate valid KMZ files compatible with DJI flight planning software
- 🎯 **Abstraction**: High-level API for easy waypoint and mission creation

## Installation

```bash
pip install djikmz
```

## Quick Start

```python
from djikmz import DroneTask

# Create a mission
mission = (DroneTask("M350", "Survey Pilot")
    .name("Basic Survey") 
    .payload("P1")
    .speed(8.0)
    .altitude(75.0)
    .fly_to(37.7749, -122.4194)
        .take_photo("point0")
        .hover(2.0)
    .fly_to(37.7750, -122.4195)
        .take_photo("point1"))

# Generate KMZ
mission.to_kmz("mission.kmz")
```

## Supported Drone Models

- M350 (Matrice 350 RTK)
- M300 (Matrice 300 RTK) 
- M30/M30T (Matrice 30 Series)
- M3E/M3T/M3M (Mavic 3 Enterprise Series)
- M3D/M3TD (Mavic 3 Classic Series)
- Other drones may be added in future releases.

## API Reference

### Task Builder API
```python
from djikmz import DroneTask

# TaskBuilder API - Primary interface
mission = DroneTask(drone_model, pilot_name)
    .payload(payload_model)  # Optional payload model
    .name(mission_name)
    .speed(m_per_sec)
    .altitude(meters)

# Flight commands  
    .fly_to(lat, lon, height=None)  # Optional height for altitude

# waypoint settings
    .height(meters)  
    .speed(m_per_sec)
    .turn_mode("turn_at_point"|"early_turn"|"curve_and_stop"|"curve_and_pass")

# Camera actions
    .take_photo(label)
    .start_recording()
    .stop_recording()

# Hover
    .hover(seconds)

# Aircraft Heading
    .heading(angle) 

# Gimbal control (absolute positioning)
    .gimbal_down(45)        # Point down to 45° from forward
    .gimbal_up(30)          # Point up to 30° from forward  
    .gimbal_front()         # Point straight forward (0°)
    .gimbal_pitch(-90)      # Precise pitch: -90° (straight down)
    .gimbal_yaw(180)        # Precise yaw: 180° (facing south)
    .gimbal_rotate(pitch=-45, yaw=90)  # Combined rotation

# Save to a ready to use Dji KMZ file
mission.to_kmz(file_path) 

# Or generate KML for further processing
mission.build() -> KML

```

### Advanced Model Access
```python
from djikmz.model import KML, Waypoint, DroneModel
from djikmz.model.action import TakePhotoAction, HoverAction

# For direct model manipulation and custom integrations
waypoint = Waypoint(lat=37.7749, lon=-122.4194)
action = TakePhotoAction(action_id=1)
```

### Validation 

DjiKMZ provides comprehensive validation:
- **Coordinates**: Latitude [-90,90], Longitude [-180,180]
- **Drone Limits**: Speed, altitude, and capability validation
- **DJI Standards**: Action IDs, waypoint limits, XML structure 

### TODOs
- Load existing KMZ files and parse waypoints
- Task modifications

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/djikmz.git
cd djikmz

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```
