import json
import machine
import time
import os

import logging
import oled
import oled.fonts.byte_bounce_14 as font


def _read_json_config(json_config_path: str) -> dict:
    with open(json_config_path, "r") as json_file:
        config = json.loads(json_file.read())
    return config


CONFIG_PATH = "/config.json"
CONFIG = _read_json_config(CONFIG_PATH)
    
LOG_FILE_PATH = "/.log"
logger = logging.Logger(verbosity=CONFIG["logger"]["verbosity"], log_file_path=LOG_FILE_PATH)
logger.debug(f"Using config {CONFIG}")


global current_mode_presses
current_mode_presses = -1
def mode_button_irq(pin):
    """System interruption handler for mode button."""
    global current_mode_presses
    current_mode_presses += 1


global current_select_press
current_select_press = False
def select_button_irq(pin):
    """System interruption handler for select button."""
    global current_select_press
    current_select_press = not current_select_press


class UI:
    """UI class - a high-level wrapper for the oled package."""
    
    INFO_FRAME_MARGIN = 1

    def __init__(self, oled: oled.Oled, animation_ticks: int):
        """Initialize animator."""
        self.oled = oled
        self.animation_ticks = animation_ticks
        self._last_ticks = time.ticks_us()
        
    @property
    def complementary_color(self):
        """Get complementary color to the background color."""
        return int(self.in_bright_mode)
        
    def dark_mode(self):
        """Switch to dark mode."""
        logger.debug("Switching to dark mode.")
        self.in_bright_mode = False
        self.oled.dark_mode()
        
    def bright_mode(self):
        """Switch to bright mode."""
        logger.debug("Switching to bright mode.")
        self.in_bright_mode = True
        self.oled.bright_mode()
        
    def clear(self):
        """Clear screen."""
        self.oled.clear()
    
    def get_frame(self, file_path: str) -> bytearray:
        """Read frame from file."""
        with open(file_path, "rb") as f:
            frame_data = f.read()
        return bytearray(frame_data)

    def get_frames_for_animation(self, animation_dir_path: str) -> list[bytearray]:
        """Read frames sequence from animation folder."""
        frames = []
        for file_name in sorted(os.listdir(animation_dir_path)):
            if file_name.endswith('.bin'):
                file_path = animation_dir_path + "/" + file_name
                frames.append(self.get_frame(file_path))
        logger.debug(f"Got {len(frames)} frames for {animation_dir_path}.")
        return frames
    
    def update_animation(self, frame_data: bytearray) -> bool:
        """Show frame of animation only if enough time has passed."""
        diff = time.ticks_diff(time.ticks_us(), self._last_ticks)
        if diff > self.animation_ticks:
            self._last_ticks = time.ticks_us()
            self.oled.display_frame(frame_data)
            return True
    
        return False # Skip frame if not enough time has passed

    def display_info(self, data: str, icon_path: str = None):
        """Display provided data on the screen."""
        y_offset = 0
        if icon_path:
            frame_data = self.get_frame(icon_path)
            self.oled.display_frame(frame_data)
            y_offset = 10
        self.oled.screen.rect(
            self.INFO_FRAME_MARGIN,	# X-coordinate of the top-left corner.
            self.INFO_FRAME_MARGIN,	# Y-coordinate of the top-left corner.
            self.oled.width - 2 * self.INFO_FRAME_MARGIN,	# Width of the rectangle.
            self.oled.height - 2 * self.INFO_FRAME_MARGIN,	# Height of the rectangle.
            self.complementary_color,
        )
        font_writer = oled.text_writer.Writer(self.oled.screen, font, verbose=False)
        font_writer.print_centered_string(data, y_offset)
        self.oled.screen.show()
        

class Device:
    """TamaGOLFchi device."""
    
    GOLFY_SHOW_MODE = "_show_golfy"
    TEMPERATURE_SHOW_MODE = "_show_temperature"
    OIL_PRESSURE_SHOW_MODE = "_show_oil_presure"
    SETTINGS_SHOW_MODE = "_show_settings"
    SHOW_MODS = [
        GOLFY_SHOW_MODE,
        TEMPERATURE_SHOW_MODE,
        OIL_PRESSURE_SHOW_MODE,
        SETTINGS_SHOW_MODE,
    ]
    
    GOLFY_HI_ANIMATION_PATH = "/animation/golfy_hi"
    GOLFY_WARN_ANIMATION_PATH = "/animation/golfy_main"
    SETTINGS_ICO_PATH = "/ico/gear.bin"
    
    def __init__(self, ui: UI):
        """Initialize utility devices."""
        logger.debug("Initializing Device.")
        self._mode_button = machine.Pin(CONFIG["control"]["mode_button_pin"], machine.Pin.IN, machine.Pin.PULL_UP)
        self._mode_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=mode_button_irq)

        self._select_button = machine.Pin(CONFIG["control"]["select_button_pin"], machine.Pin.IN, machine.Pin.PULL_UP)
        self._select_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=select_button_irq)

        self._show_mode_index = 0
        self._ui = ui
        self._ui.bright_mode()
    
    @property
    def _current_show_mode(self) -> str:
        """Return current show mode, if mode button is pressed loop over modes."""
        self._show_mode_index = (current_mode_presses + 1) % len(self.SHOW_MODS)
        return self.SHOW_MODS[self._show_mode_index]
    
    @property
    def _current_select_mode(self) -> bool:
        """Return a flag for select button."""
        return current_select_press
    
    def _play_animation_no_brake(self, animation_path: str, play_once: bool = True):
        """Play animation (once or in a loop) without interruptions."""
        logger.debug(f"Showing {animation_path}.")
        
        frames = self._ui.get_frames_for_animation(animation_path)
        frame_index = 0
        while True:
            updated = self._ui.update_animation(frames[frame_index])
            if updated:
                logger.debug(f"Updated frame #{frame_index}")
                frame_index += 1
                if frame_index + 1 > len(frames) and not play_once:
                    frame_index = 0
                elif frame_index + 1 > len(frames):
                    break  
            
    def _play_animation_loop(self, animation_path: str):
        """Play animation loop listening `last_show_mode` changes."""
        last_show_mode = self._current_show_mode
        logger.debug(f"Showing {last_show_mode} mode, {animation_path}.")
        
        last_mode = self._current_show_mode
        frames = self._ui.get_frames_for_animation(animation_path)
        
        frame_index = 0
        while True:
            if self._current_show_mode != last_mode:
                break
            updated = self._ui.update_animation(frames[frame_index])
            if updated:
                logger.debug(f"Updated frame #{frame_index}")
                frame_index += 1
                if frame_index + 1 > len(frames):
                    frame_index = 0
                    
    def play_hello_animation(self):
        """Play hello animation, all controls are disabled."""
        logger.debug("Playing hello animation...")
        self._play_animation_no_brake(self.GOLFY_HI_ANIMATION_PATH)
            
    def _show_golfy(self):
        """Play Golfy animation and return when mode switched."""
        logger.debug("Showing Golfy.")
        self._play_animation_loop(self.GOLFY_WARN_ANIMATION_PATH)
                
    def _show_temperature(self):
        """Show temperature and return when mode switched."""
        logger.debug("Showing temperature.")
        last_show_mode = self._current_show_mode
        self._ui.clear()
        self._ui.display_info("92\n'C ")
        while True: 
            if last_show_mode != self._current_show_mode:
                return
    
    def _show_oil_presure(self):
        """Show temperature and return when mode switched."""
        logger.debug("Showing oil pressure.")
        last_show_mode = self._current_show_mode
        self._ui.clear()
        self._ui.display_info("7.5\nBAR")
        while True:
            if last_show_mode != self._current_show_mode:
                return
            
    def _show_settings(self):
        """Show settings and return when mode switched."""
        logger.debug("Showing settings.")
        last_show_mode = self._current_show_mode
        last_select_mode = self._current_select_mode
        self._ui.clear()
        self._ui.display_info("SETT", self.SETTINGS_ICO_PATH)
        settings_list = [
            "BRT",
            "MODE",
        ]
        current_settings_index = 0
        while True:
            if last_show_mode != self._current_show_mode:
                return
            if last_select_mode != self._current_select_mode:
                self._ui.clear()
                text = settings_list[current_settings_index]
                self._ui.display_info(text)
                current_settings_index = (current_settings_index + 1) % len(settings_list)
                last_select_mode = self._current_select_mode
    
    def run(self):
        """Run device main loop."""
        while True:
            getattr(self, self._current_show_mode)()
            
        

def main():
    """Run loop with exception logging."""
    with logger:
        oled_screen = oled.Oled(**CONFIG["oled"])
        ui = UI(oled=oled_screen, animation_ticks=CONFIG["ui"]["animation_ticks"])
        dev = Device(ui=ui)
        dev.play_hello_animation()
        dev.run()


if __name__ == "__main__":
    main()
    