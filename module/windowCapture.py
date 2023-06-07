from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
from time import time

import numpy as np
import win32gui

GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
SRCCOPY = 0x00CC0020
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC

# 排除缩放干扰
windll.user32.SetProcessDPIAware()


class WindowCapture:
    def __init__(self, window_name):
        # 找到要截图的窗口句柄
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('找不到不到窗口: {}'.format(window_name))

    def get_screenshot(self):
        """窗口客户区截图

           Args:
               handle (HWND): 要截图的窗口句柄

           Returns:
               numpy.ndarray: 截图数据
           """
        # 获取窗口客户区的大小
        r = RECT()
        GetClientRect(self.hwnd, byref(r))
        width, height = r.right, r.bottom
        # 开始截图
        dc = GetDC(self.hwnd)
        cdc = CreateCompatibleDC(dc)
        bitmap = CreateCompatibleBitmap(dc, width, height)
        SelectObject(cdc, bitmap)
        BitBlt(cdc, 0, 0, width, height, dc, 0, 0, SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = width * height * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        DeleteObject(bitmap)
        DeleteObject(cdc)
        ReleaseDC(self.hwnd, dc)
        # 返回截图数据为numpy.ndarray
        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

    def list_window_names(self):
        # 获取所有打开的窗口每次列表
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(winEnumHandler, None)

    def save_image(self, file):
        cv.imwrite(file + '.png', self.get_screenshot())


if __name__ == '__main__':
    import cv2 as cv

    wincap = WindowCapture('剑网3系列启动器')
    # wincap.list_window_names()
    # screenshot = wincap.get_screenshot()

    loop_time = time()
    while True:
        screenshot = wincap.get_screenshot()
        cv.imshow('capture vision', screenshot)
        print('FPS {}'.format(1 / (time() - loop_time)))
        loop_time = time()

        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break
