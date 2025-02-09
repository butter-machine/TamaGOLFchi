from machine import Pin, SoftI2C
import ssd1306


class Oled:
    """OLED module class."""
    def __init__(self, i2c_scl_pin: int, i2c_sda_pin: int, height_pxls: int, width_pxls: int, frequency: int):
        """Connect OLED by I2C."""
        self.i2c = SoftI2C(
            scl=Pin(i2c_scl_pin),
            sda=Pin(i2c_sda_pin),
            freq=frequency,
        )
        self.height = height_pxls
        self.width = width_pxls
        self.screen = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)
    
    def dark_mode(self):
        """Switch to dark mode - backlight is off."""
        self.screen.invert(0)
    
    def bright_mode(self):
        """Switch to dark mode - backlight is on."""
        self.screen.invert(1)
        
    def display_frame(
        self,
        frame_data: bytearray,
        frame_width: int,
        frame_height: int,
        x_offset: int = 0,
        y_offset: int = 0,
    ):
        """Display a single frame on the OLED screen, centered."""
        self.screen.fill(0)  # Clear the screen

        byte_index = 0
        for y in range(frame_height):
            for x in range(frame_width):
                byte_value = frame_data[byte_index]
                pixel = (byte_value >> (7 - (x % 8))) & 1  # Extract bit for pixel
                if pixel:
                    self.screen.pixel(x + x_offset, y + y_offset, 1)
                if (x + 1) % 8 == 0:
                    byte_index += 1
        self.screen.show()
