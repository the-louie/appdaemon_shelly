# AppDaemon Shelly Integration

A Python-based AppDaemon integration for connecting Shelly devices to Home Assistant via MQTT. This project provides seamless control of Home Assistant lights through Shelly input devices.

## Features

- **MQTT Integration**: Connects to Shelly devices via MQTT protocol
- **Flexible Control Modes**: Supports both toggle and direct on/off control
- **Robust Error Handling**: Comprehensive error handling and logging
- **Type Safety**: Full type hints for better code maintainability
- **Multiple Device Support**: Configure multiple Shelly devices independently

## Prerequisites

- [AppDaemon](https://appdaemon.readthedocs.io/en/latest/) installed and configured
- [Home Assistant](https://www.home-assistant.io/) running with MQTT integration
- Shelly devices configured to publish to MQTT topics
- Python 3.8 or higher

## Installation

1. **Clone or download this repository** to your AppDaemon apps directory:
   ```bash
   cd /path/to/appdaemon/apps
   git clone <repository-url> appdaemon_shelly
   ```

2. **Copy the configuration template**:
   ```bash
   cp config.yaml.example config.yaml
   ```

3. **Edit the configuration** file with your specific device details (see Configuration section below)

4. **Restart AppDaemon** to load the new app

## Configuration

Edit `config.yaml` with your Shelly device details:

```yaml
# Shelly Input to Light Control
shelly_test:
  module: i1_shelly
  class: MQTT
  topic: "shellies/shellyix3-ABCDEFGH0123456/input/0"  # Your Shelly device topic
  light: light.ceiling_lamp  # Your Home Assistant light entity
  toggle: true  # true for toggle mode, false for direct control

# Multiple devices example
shelly_kitchen:
  module: i1_shelly
  class: MQTT
  topic: "shellies/shellyix3-KITCHEN123/input/0"
  light: light.kitchen_ceiling
  toggle: false

shelly_living_room:
  module: i1_shelly
  class: MQTT
  topic: "shellies/shellyix3-LIVING456/input/0"
  light: light.living_room_lamp
  toggle: true
```

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | Yes | MQTT topic to listen for (e.g., "shellies/device-id/input/0") |
| `light` | string | Yes | Home Assistant light entity to control |
| `toggle` | boolean | No | Control mode: `true` for toggle, `false` for direct on/off (default: `false`) |

## Usage

### Toggle Mode (`toggle: true`)
- Each input event toggles the light state
- Press once: turn on, press again: turn off
- Ideal for single-button switches

### Direct Mode (`toggle: false`)
- Input state directly controls light state
- Input 0 = light off, Input 1 = light on
- Ideal for momentary switches or sensors

## MQTT Topic Format

The expected MQTT topic format is:
```
shellies/{device-id}/input/{input-number}
```

Where:
- `{device-id}` is your Shelly device's unique identifier
- `{input-number}` is the input number (usually 0 for single-input devices)

## Troubleshooting

### Common Issues

1. **App not loading**: Check AppDaemon logs for configuration errors
2. **MQTT not connecting**: Verify MQTT broker settings in AppDaemon configuration
3. **No light control**: Ensure the light entity exists in Home Assistant
4. **Wrong topic**: Verify the MQTT topic matches your Shelly device configuration

### Debug Logging

Enable debug logging in AppDaemon to see detailed MQTT message handling:

```yaml
# In your AppDaemon configuration
log_level: DEBUG
```

## Development

### Project Structure

```
appdaemon_shelly/
├── i1_shelly.py          # Main AppDaemon app
├── config.yaml.example   # Configuration template
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

### Code Quality

This project follows Python best practices:
- Type hints for all functions and variables
- Comprehensive error handling
- Detailed logging with appropriate levels
- Clear documentation and comments
- Consistent code style

### Testing

To test the integration:

1. Configure a test device in `config.yaml`
2. Monitor AppDaemon logs for initialization messages
3. Trigger your Shelly device and verify light control
4. Check logs for any error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type hints and documentation
4. Test thoroughly
5. Submit a pull request

## License

MIT License - Copyright (c) 2024 the_louie - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review AppDaemon logs for error messages
3. Verify your Shelly device MQTT configuration
4. Open an issue on the project repository

## Changelog

### Version 1.0.0
- Initial release
- MQTT integration with Shelly devices
- Toggle and direct control modes
- Comprehensive error handling and logging
- Type hints and documentation