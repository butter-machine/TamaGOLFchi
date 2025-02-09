import json
import time

import logging
from oled import Oled, OledAnimator


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

    def __init__(self, animator: OledAnimator):
        """Initialize utility devices."""
        logger.debug(f"Initializing Device.")
        self.animator = animator


def main():
    """Run loop with exception logging."""
    with logger:
        oled = Oled(**CONFIG["oled"])
        animator = OledAnimator(oled=oled, animation_fps=CONFIG["ui"]["animation_fps"])
        dev = Device(animator=animator)
        dev.animator.bright_mode()
        while True:
            dev.animator.bright_mode()
            dev.animator.display_info("23 C")
            time.sleep(1)
            dev.animator.dark_mode()
            dev.animator.display_info("23 C")
            time.sleep(1)
        

if __name__ == "__main__":
    main()
    