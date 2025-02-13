import time
import io

import oled.text_writer as text_writer
import oled.fonts.byte_bounce_14 as font


class OledAnimator:
    """
    Oled animation player.
    
    How to play animation:
    animator = OledAnimator(oled, 24)
    with open(animation_path, "rb") as file:
        animator.clear()	# Make sure to clear screen before showing animation.
        frame = ""	# Initial non-None value.
        while frame is not None:
            frame = animator.get_frame_data_from_file(file)
            animator.update_animation(frame)
    """
    
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
        
    def clear(self):
        """Clear screen."""
        self.oled.clear()
        
    def get_frame_data_from_file(self, file: io.BufferedReader):
        """Get next frame from opened file"""
        return file.read(self.oled.width * self.oled.height // 8)
    
    def update_animation(self, frame_data: str):
        """Show frame of animation."""
        self.oled.display_frame(frame_data, self.oled.width, self.oled.height)
        time.sleep(1 / self.animation_fps)	# TODO

    def display_info(self, data: str):
        """Display provided data on the screen."""
        self.oled.screen.rect(
            self.INFO_FRAME_MARGIN,	# X-coordinate of the top-left corner.
            self.INFO_FRAME_MARGIN,	# Y-coordinate of the top-left corner.
            self.oled.width - 2 * self.INFO_FRAME_MARGIN,	# Width of the rectangle.
            self.oled.height - 2 * self.INFO_FRAME_MARGIN,	# Height of the rectangle.
            self.complementary_color,
        )
        font_writer = text_writer.Writer(self.oled.screen, font)
        font_writer.print_centered_string(data)
        self.oled.screen.show()
