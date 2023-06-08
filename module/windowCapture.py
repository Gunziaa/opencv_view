from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
from time import time

import numpy as np
import win32api
import win32con
import win32gui
import win32ui

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
    """参数可以是 :

    -窗口句柄,

    -窗口标题,

    -par = 0  表示全屏截图 ,

    -par = (x, y, width, height) 表示指定区域截图

    """
    def __init__(self, par):
        self.y = 0
        self.x = 0
        if par == 0:  # 全屏截图
            self.hwnd = par
            # 获取屏幕的宽度和高度
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        elif isinstance(par, tuple) or isinstance(par, list):  # 认为是指定区域截图  参数= (x,y,width,height)
            self.hwnd = 0
            self.x = par[0]
            self.y = par[1]
            self.width = par[2]
            self.height = par[3]

        elif par > 0:  # par 大于0 认为是窗口句柄
            self.hwnd = par
            r = RECT()
            GetClientRect(self.hwnd, byref(r))
            self.width, self.height = r.right, r.bottom

        elif isinstance(par, str):
            # 找到要截图的窗口句柄
            self.hwnd = win32gui.FindWindow(None, par)
            # 获取窗口客户区的大小
            r = RECT()
            GetClientRect(self.hwnd, byref(r))
            self.width, self.height = r.right, r.bottom
            if not self.hwnd:
                raise Exception('找不到不到窗口: {}'.format(par))

    def screenshot(self):
        """窗口客户区截图
           Returns:
               numpy.ndarray: 截图数据
           """
        # 获取窗口客户区的大小
        # 开始截图
        # 此方法获取的图片格式为 BGRA
        dc = GetDC(self.hwnd)
        cdc = CreateCompatibleDC(dc)
        bitmap = CreateCompatibleBitmap(dc, self.width, self.height)
        SelectObject(cdc, bitmap)
        BitBlt(cdc, 0, 0, self.width, self.height, dc, self.x, self.y, SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = self.width * self.height * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        DeleteObject(bitmap)
        DeleteObject(cdc)
        ReleaseDC(self.hwnd, dc)
        # 返回截图数据为numpy.ndarray
        img = np.frombuffer(buffer, dtype=np.uint8).reshape(self.height, self.width, 4)
        return img

    def save_screenshot(self, file):
        """保存截图"""
        cv.imwrite(file + '.png', self.screenshot())


if __name__ == '__main__':
    import cv2 as cv

    wincap = WindowCapture(0)
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
