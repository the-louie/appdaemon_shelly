"""
Shelly MQTT Integration for AppDaemon

This module provides integration between Shelly devices and Home Assistant
through MQTT messages. It handles input events from Shelly devices and
controls Home Assistant lights accordingly.

Author: the_louie
License: MIT
"""

import appdaemon.plugins.hass.hassapi as hass
import time
import json
from typing import Optional, Dict, Any, Union
import logging


class MQTT(hass.Hass):
    """
    AppDaemon app for integrating Shelly devices with Home Assistant via MQTT.

    This class handles MQTT messages from Shelly input devices and controls
    Home Assistant lights based on the input state changes.

    Configuration:
        topic (str): MQTT topic to listen for (e.g., "shellies/device-id/input/0")
        light (str): Home Assistant light entity to control
        toggle (bool): If True, toggle light state; if False, direct on/off control
    """

    def initialize(self) -> None:
        """
        Initialize the MQTT integration.

        Sets up MQTT subscription, validates configuration, and registers
        event listeners for MQTT messages.

        Raises:
            ValueError: If required configuration is missing
        """
        self.log('Shelly MQTT Integration: Initializing...', level="INFO")

        # Initialize MQTT connection
        try:
            self.mqtt = self.get_plugin_api("MQTT")
            self.mqtt.mqtt_subscribe('shellies/#')
        except Exception as e:
            self.log(f'Shelly MQTT Integration: Failed to initialize MQTT: {e}', level="ERROR")
            raise

        # Load configuration
        self._load_configuration()

        # Validate configuration
        self._validate_configuration()

        # Initialize state tracking
        self.last_state: Optional[str] = None
        self.last_event: int = 0

        # Register event listener
        self.mqtt.listen_event(self._handle_shelly_event, "MQTT_MESSAGE")

        # Log initial light state
        initial_state = self.get_state(self.light)
        self.log(f'Shelly MQTT Integration: Initial light state for {self.light}: {initial_state}', level="DEBUG")

        if self.mqtt.is_client_connected():
            self.log('Shelly MQTT Integration: MQTT client connected successfully', level="INFO")
        else:
            self.log('Shelly MQTT Integration: MQTT client not connected', level="WARNING")

    def _load_configuration(self) -> None:
        """Load and store configuration parameters."""
        self.topic: Optional[str] = self.args.get("topic")
        self.light: Optional[str] = self.args.get("light")
        self.toggle: bool = self.args.get("toggle", False)

    def _validate_configuration(self) -> None:
        """
        Validate that all required configuration parameters are present.

        Raises:
            ValueError: If required configuration is missing
        """
        if self.topic is None:
            raise ValueError("Missing required configuration: 'topic'")
        if self.light is None:
            raise ValueError("Missing required configuration: 'light'")

        self.log(f'Shelly MQTT Integration: Configuration validated - Topic: {self.topic}, Light: {self.light}, Toggle: {self.toggle}', level="DEBUG")

    def _handle_shelly_event(self, event_name: str, data: Dict[str, Any], kwargs: Dict[str, Any]) -> None:
        """
        Handle incoming MQTT messages from Shelly devices.

        Args:
            event_name: The name of the event (should be "MQTT_MESSAGE")
            data: Dictionary containing MQTT message data
            kwargs: Additional keyword arguments
        """
        # Validate data structure
        if data is None:
            self.log('Shelly MQTT Integration: Received empty MQTT data', level="WARNING")
            return

        # Check if this message is for our configured topic
        topic = data.get('topic')
        if topic is None:
            # This is likely a connection status message, ignore it
            self.log('Shelly MQTT Integration: Received MQTT message without topic (connection status)', level="DEBUG")
            return

        if not topic.startswith(self.topic):
            # Not our topic, ignore it
            return

        # Extract payload
        new_state = data.get("payload")
        if new_state is None:
            self.log(f'Shelly MQTT Integration: Invalid payload in MQTT message: {data}', level="ERROR")
            return

        self.log(f'Shelly MQTT Integration: Received state change - Topic: {topic}, New State: {new_state}', level="DEBUG")

        # Handle first message (initialize state)
        if self.last_state is None:
            self.log(f'Shelly MQTT Integration: Initializing state to: {new_state}', level="DEBUG")
            self.last_state = new_state
            return

        # Check if state actually changed
        if new_state == self.last_state:
            self.log(f'Shelly MQTT Integration: No state change detected: {new_state}', level="DEBUG")
            return

        # Update timestamp
        self.last_event = int(time.time())

        # Handle state change based on toggle mode
        try:
            if self.toggle:
                self._handle_toggle_mode(new_state)
            else:
                self._handle_direct_mode(new_state)
        except Exception as e:
            self.log(f'Shelly MQTT Integration: Error handling state change: {e}', level="ERROR")
            return

        # Update last state
        self.last_state = new_state

    def _handle_toggle_mode(self, new_state: str) -> None:
        """
        Handle state change in toggle mode.

        Args:
            new_state: The new state received from the Shelly device
        """
        self.log(f'Shelly MQTT Integration: Toggle mode - toggling light {self.light}', level="INFO")
        self._toggle_light()

    def _handle_direct_mode(self, new_state: str) -> None:
        """
        Handle state change in direct mode.

        Args:
            new_state: The new state received from the Shelly device
        """
        try:
            state_value = int(new_state)
            if state_value == 0:
                self.log(f'Shelly MQTT Integration: Direct mode - turning off {self.light}', level="INFO")
                self.turn_off(self.light)
            else:
                self.log(f'Shelly MQTT Integration: Direct mode - turning on {self.light}', level="INFO")
                self.turn_on(self.light)
        except ValueError:
            self.log(f'Shelly MQTT Integration: Invalid state value for direct mode: {new_state}', level="ERROR")

    def _toggle_light(self) -> None:
        """
        Toggle the light state (on/off).

        Handles the toggle operation by checking current state and switching
        to the opposite state.
        """
        try:
            current_state = self.get_state(self.light)

            if current_state == 'on':
                self.log(f'Shelly MQTT Integration: Toggling {self.light} from ON to OFF', level="DEBUG")
                self.turn_off(self.light)
            elif current_state == 'off':
                self.log(f'Shelly MQTT Integration: Toggling {self.light} from OFF to ON', level="DEBUG")
                self.turn_on(self.light)
            else:
                self.log(f'Shelly MQTT Integration: Unknown light state "{current_state}" for {self.light}', level="WARNING")
                # Default to turning on if state is unknown
                self.turn_on(self.light)

        except Exception as e:
            self.log(f'Shelly MQTT Integration: Error toggling light {self.light}: {e}', level="ERROR")


