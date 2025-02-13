"""Button press processing."""
import machine


class Button:
    """A button class."""
    
    last_value: bool | None = None
    
    def __init__(self, pin: int, identity: str):
        """Initialize."""
        self._pin = pin
        self._identity = identity
        self._button = machine.Pin(self._pin, machine.Pin.IN, machine.Pin.PULL_UP)
        
    def _get_value(self) -> bool:
        """Get value converting to bool - True if pressed, False if released."""
        return not bool(self._button.value())
    
    @property
    def value(self) -> bool:
        """Get current value."""
        self.last_value = self._get_value()
        return self.last_value
    
    @property
    def on_press(self) -> bool:
        """Return True if button was pressed once."""
        last = self.last_value
        curr = self.value
        return not last and curr
    
    @property
    def on_release(self) -> bool:
        """Return True if button was pressed and released (still False if just pressed)."""
        last = self.last_value
        curr = self.value
        return last and not curr
                