import json
import time
import machine

import logging
from oled import Oled, OledAnimator
from button import Button


def _read_json_config(json_config_path: str) -> dict:
    with open(json_config_path, "r") as json_file:
        config = json.loads(json_file.read())
    return config


CONFIG_PATH = "/config.json"
CONFIG = _read_json_config(CONFIG_PATH)
    
LOG_FILE_PATH = "/.log"
logger = logging.Logger(verbosity=CONFIG["logger"]["verbosity"], log_file_path=LOG_FILE_PATH)
logger.debug(f"Using config {CONFIG}")



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
    
    GOLFY_HI_ANIMATION_PATH = "/animation/golfy_hi.bin"
    GOLFY_WARN_ANIMATION_PATH = "/animation/golfy_warn.bin"
    
    def __init__(self, animator: OledAnimator):
        """Initialize utility devices."""
        logger.debug("Initializing Device.")
        self._animator = animator
        self._animator.bright_mode()
        self._mode_button = Button(pin=CONFIG["control"]["mode_button_pin"], identity="mode_btn")
        self._select_button = Button(pin=CONFIG["control"]["select_button_pin"], identity="sel_btn")
        self._show_mode_index = 0
        
    def play_hello_animation(self):
        """Play hello animation, all controls are disabled."""
        frame = "initial"
        with open(self.GOLFY_HI_ANIMATION_PATH, "rb") as file:
            while frame is not None:
                frame = self._animator.get_frame_data_from_file(file)
                if not frame:
                    break
                self._animator.update_animation(frame)
    
    @property
    def _current_show_mode(self) -> str:
        """Return current show mode, if mode button is pressed loop over modes."""
        if self._mode_button.on_press:
            self._show_mode_index = (self._show_mode_index + 1) % len(self.SHOW_MODS)
        return self.SHOW_MODS[self._show_mode_index]
            
    def _play_animation(self, animation_path: str):
        """Play animation."""
        last_show_mode = self._current_show_mode
        logger.debug(f"Showing {last_show_mode} mode, {animation_path}.")
        
        frame_index = 0
        frame = "initial"
        with open(animation_path, "rb") as file:
            while frame is not None:
                if last_show_mode != self._current_show_mode:
                    break
                logger.debug(f"Playing frame {frame_index}")
                frame_index += 1
                frame = self._animator.get_frame_data_from_file(file)
                if not frame:
                    break
                self._animator.update_animation(frame)
                
    def _show_golfy(self):
        """Play Golfy animation and return when mode switched."""
        self._play_animation(self.GOLFY_WARN_ANIMATION_PATH)
        
                
    def _show_temperature(self):
        """Show temperature and return when mode switched."""
        last_show_mode = self._current_show_mode
        logger.debug(f"Showing {last_show_mode} mode.")
        self._animator.clear()
        self._animator.display_info("92\n'C ")
        while True: 
            if last_show_mode != self._current_show_mode:
                return
    
    def _show_oil_presure(self):
        """Show temperature and return when mode switched."""
        last_show_mode = self._current_show_mode
        logger.debug(f"Showing {last_show_mode} mode.")
        self._animator.clear()
        self._animator.display_info("7.5\nBAR")
        while True:
            if last_show_mode != self._current_show_mode:
                return
            
    def _show_settings(self):
        """Show settings and return when mode switched."""
        last_show_mode = self._current_show_mode
        logger.debug(f"Showing {last_show_mode} mode.")
        self._animator.clear()
        self._animator.display_info("SET\nUPS")
        settings_list = [
            "brtns",
            "smth",
            "else",
        ]
        current_settings_index = 0
        while True:
            if last_show_mode != self._current_show_mode:
                return
            if self._select_button.on_press:
                self._animator.clear()
                text = settings_list[current_settings_index]
                self._animator.display_info(text)
                current_settings_index = (current_settings_index + 1) % len(settings_list)
    
    def run(self):
        """Run device main loop."""
        while True:
            getattr(self, self._current_show_mode)()
            
        

def main():
    """Run loop with exception logging."""
    with logger:
        oled = Oled(**CONFIG["oled"])
        animator = OledAnimator(oled=oled, animation_fps=CONFIG["ui"]["animation_fps"])
        dev = Device(animator=animator)
        dev.play_hello_animation()
        dev.run()


if __name__ == "__main__":
    main()
    