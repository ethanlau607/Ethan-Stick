from ssd1306 import SSD1306_I2C

SET_HWSCROLL_OFF    = const(0x2e)
SET_HWSCROLL_ON     = const(0x2f)
SET_HWSCROLL_RIGHT  = const(0x26)
SET_HWSCROLL_LEFT   = const(0x27)
SET_HWSCROLL_VR     = const(0x29)
SET_HWSCROLL_VL     = const(0x2a)

class SSD1306_I2C_FLAG(SSD1306_I2C):
    FRAMES_2 = 0x07
    FRAMES_3 = 0x04
    FRAMES_4 = 0x05
    FRAMES_5 = 0x00
    FRAMES_25 = 0x06
    FRAMES_64 = 0x01
    FRAMES_128 = 0x02
    FRAMES_256 = 0x03
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        super().__init__(width, height, i2c, addr, external_vcc)
        
    def clear(self):
        self.fill(0)
        self.show()
    
    def hw_scroll_off(self):
        self.write_cmd(SET_HWSCROLL_OFF) # turn off scroll
        
    def hw_scroll_h(
        self, 
        direction=True,    # True/False: right/left
        interval=FRAMES_5  # one frame ��� 9.2ms
    ):
        self.write_cmd(SET_HWSCROLL_OFF)  # turn off hardware scroll per SSD1306 datasheet
        if not direction:
            self.write_cmd(SET_HWSCROLL_LEFT)
        else:
            self.write_cmd(SET_HWSCROLL_RIGHT)
        self.write_cmd(0x00)            # dummy byte
        self.write_cmd(0x00)            # start page = page 0
        self.write_cmd(interval)        # interval
        self.write_cmd(0x07)            # end page = page 7
        self.write_cmd(0x00)            # dummy byte
        self.write_cmd(0xff)            # dummy byte
        self.write_cmd(SET_HWSCROLL_ON) # activate scroll

    def hw_scroll_diag(
        self, 
        direction=True,    # True/False: right/left
        interval=FRAMES_5, # one frame ��� 9.2ms
        offset=1           # vertical offset per scroll
    ):

        self.write_cmd(SET_HWSCROLL_OFF)  # turn off hardware scroll per SSD1306 datasheet
        if not direction:
            self.write_cmd(SET_HWSCROLL_VL)
        else:
            self.write_cmd(SET_HWSCROLL_VR)
        self.write_cmd(0x00)            # dummy byte
        self.write_cmd(0x00)            # start page = page 0
        self.write_cmd(interval)        # interval
        self.write_cmd(0x07)            # end page = page 7
        self.write_cmd(offset)          # vertical offset per scroll
        self.write_cmd(SET_HWSCROLL_ON) # activate scroll