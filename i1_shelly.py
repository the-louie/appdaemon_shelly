import appdaemon.plugins.hass.hassapi as hass
import time
import json

class MQTT(hass.Hass):
    def initialize(self):
        self.log('i1 Shelly MQTT loading...')
        self.mqtt = self.get_plugin_api("MQTT")
        self.mqtt.mqtt_subscribe('shellies/#')

        self.topic = self.args.get("topic")
        self.light = self.args.get("light")
        self.toggle = self.args.get("toggle", False)
        self.last_event = int(0)

        if (self.topic is None or self.light is None):
            self.log("i1 Missing configuration")
            return

        self.last_state = None #self.get_initial_state(self.light)

        if self.mqtt.is_client_connected():
            self.log('i1 MQTT is connected')

        self.mqtt.listen_event(self.shelly_event, "MQTT_MESSAGE")

        a = self.get_state(self.light)
        #self.log('i1 DEBUG self.light ({}) state = "{}"'.format(self.light, a))

    def shelly_event(self, event_name, data, kwargs):
        if data is not None and not (data.get('topic','')).startswith(self.topic):
            return
        new_state = data.get("payload")
        #self.log('i1 DEBUG shelly_event(self, {}, {}, kwargs)'.format(event_name, data))
        if new_state is None:
            self.log('i1 ERROR: {}'.format(data))
            return
        if self.last_state is None:
            # if this is the first message assume that the button WASN't clicked but that it's just an update
            # and set it as the current state.
            #self.log('i1 DEBUG last_state = None => {}'.format(new_state))
            self.last_state = new_state
            return
        if new_state == self.last_state:
            #self.log('i1 DEBUG {} == {} (no change)'.format(new_state, self.last_state))
            return

        #self.log('i1 DEBUG data={}'.format(json.dumps(data)));

        self.last_event = int(time.time())

        if self.toggle and new_state != self.last_state:
            self.toggle_light()
            self.last_state = new_state
            return

        if not self.toggle and new_state != self.last_state:
            if new_state == 0:
                self.turn_off(self.light)
            else:
                self.turn_on(self.light)
            self.last_state = new_state
            return

        self.log("i1 CRITICAL: we got lost")


    def toggle_light(self):
        curr_state = self.get_state(self.light)
        if curr_state == 'on':
            self.turn_off(self.light)
        elif curr_state == 'off':
            self.turn_on(self.light)
        else:
            self.log("i1 unknown state '{}' for {}".format(curr_state, self.light))


