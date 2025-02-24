"""
Print text from font.

Based on https://github.com/peterhinch/micropython-font-to-py/tree/master
"""
import framebuf

class Writer():
    """A class to write a font."""
    
    text_row = 0        # attributes common to all Writer instances
    text_col = 0
    row_clip = False    # Clip or scroll when screen full
    col_clip = False    # Clip or new line when row is full

    @classmethod
    def set_textpos(cls, col, row):
        cls.text_row = row
        cls.text_col = col

    @classmethod
    def set_clip(cls, col_clip, row_clip):
        cls.row_clip = row_clip
        cls.col_clip = col_clip

    def __init__(self, device, font, verbose=True):
        self.device = device
        self.font = font
        # Allow to work with any font mapping
        if font.hmap():
            self.map = framebuf.MONO_HMSB if font.reverse() \
                else framebuf.MONO_HLSB
        else:
            raise ValueError('Font must be horizontally mapped.')
        if verbose:
            print('Orientation: {} Reversal: {}'.format('horiz' \
                if font.hmap() else 'vert', font.reverse()))
        self.screenwidth = device.width  # In pixels
        self.screenheight = device.height

    def _newline(self):
        height = self.font.height()
        Writer.text_row += height
        Writer.text_col = 0
        margin = self.screenheight - (Writer.text_row + height)
        if margin < 0:
            if not Writer.row_clip:
                self.device.scroll(0, margin)
                Writer.text_row += margin

    def printstring(self, string):
        for char in string:
            self._printchar(char)

    # Method using blitting. Efficient rendering for monochrome displays.
    # Tested on SSD1306. Invert is for black-on-white rendering.
    def _printchar(self, char, invert=False):
        if char == '\n':
            self._newline()
            return
        glyph, char_height, char_width = self.font.get_ch(char)
        if Writer.text_row + char_height > self.screenheight:
            if Writer.row_clip:
                return
            self._newline()
        if Writer.text_col + char_width > self.screenwidth:
            if Writer.col_clip:
                return
            else:
                self._newline()
        buf = bytearray(glyph)
        if invert:
            for i, v in enumerate(buf):
                buf[i] = 0xFF & ~ v
        fbc = framebuf.FrameBuffer(buf, char_width, char_height, self.map)
        self.device.blit(fbc, Writer.text_col, Writer.text_row)
        Writer.text_col += char_width

    def stringlen(self, string):
        l = 0
        for char in string:
            l += self._charlen(char)
        return l

    def _charlen(self, char):
        if char == '\n':
            char_width = 0
        else:
            _, _, char_width = self.font.get_ch(char)
        return char_width
    
    def get_text_dimensions(self, string):
        """Calculate total width and height of the text to center it."""
        width = 0
        height = 0
        lines = string.split("\n")
        max_line_height = 0  # Track the maximum height of any line

        # Calculate total width (longest line) and total height (sum of line heights)
        for line in lines:
            line_width = 0
            for char in line:
                _, char_height, char_width = self.font.get_ch(char)
                line_width += char_width
                if char_height > max_line_height:
                    max_line_height = char_height
            width = max(width, line_width)  # The longest line determines the width
            height += max_line_height  # Sum the height of all lines
        return width, height, max_line_height

    def center_text(self, string):
        """Calculate position to center the text, handling multiple lines."""
        lines = string.split("\n")
        width, total_height, max_line_height = self.get_text_dimensions(string)

        # Center horizontally
        x_pos = (self.screenwidth - width) // 2

        # Center vertically, distributing space evenly for all lines
        y_pos = (self.screenheight - total_height) // 2

        return x_pos, y_pos, max_line_height, len(lines)

    def print_centered_string(self, string, y_offset=0):
        """Print the string centered on the screen, with correct spacing for multiple lines."""
        x_pos, y_pos, max_line_height, num_lines = self.center_text(string)
        lines = string.split("\n")

        # Print each line centered individually
        for i, line in enumerate(lines):
            self.set_textpos(x_pos, y_pos + (max_line_height * i) + y_offset)
            self.printstring(line)
