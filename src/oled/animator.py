import time

import oled.text_writer as text_writer
import oled.fonts.freesans20 as freesans20


class OledAnimator:
    """Oled animation player."""
    INFO_FRAME_MARGIN = 3

    def __init__(self, oled: Oled, animation_fps: int):
        """Initialize animator."""
        self.oled = oled
        self.animation_fps = animation_fps
        self.in_bright_mode = True
        self.bright_mode()
        
    @property
    def complementary_color(self):
        """Get complementary color to the background color."""
        return int(self.in_bright_mode)
        
    def dark_mode(self):
        """Switch to dark mode."""
        self.oled.dark_mode()
        
    def bright_mode(self):
        """Switch to bright mode."""
        self.oled.bright_mode()
        
    def display_animation(self, animation_path: str):
        """Play animation from .bin file."""
        with open(animation_path, 'rb') as f:
            while True:
                frame_data = f.read(self.oled.width * self.oled.height // 8)
                if len(frame_data) == 0:
                    break
                self.oled.display_frame(frame_data, self.oled.width, self.oled.height)
                time.sleep(1 / self.animation_fps)

    def display_info(self, data: str):
        self.oled.screen.rect(
            self.INFO_FRAME_MARGIN,	# X-coordinate of the top-left corner.
            self.INFO_FRAME_MARGIN,	# Y-coordinate of the top-left corner.
            self.oled.width - 2 * self.INFO_FRAME_MARGIN,	# Width of the rectangle.
            self.oled.height - 2 * self.INFO_FRAME_MARGIN,	# Height of the rectangle.
            self.complementary_color,
        )
        font_writer = text_writer.Writer(self.oled.screen, freesans20)
        font_writer.set_textpos(14, 25)
        font_writer.printstring("79")
        self.oled.screen.show()
