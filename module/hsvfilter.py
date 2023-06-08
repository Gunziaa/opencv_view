import json

import cv2 as cv
from time import sleep

import numpy as np


class HsvFilter:
    TRACKBAR_WINDOW = "Trackbars"

    def __init__(self):
        self.window_w = 400
        self.window_h = 600

    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, self.window_w, self.window_h)

        # 我们将使用 getTrackbarPos（） 进行查找，而不是使用回调。
        def nothing(position):
            pass

        # 创建用于包围的跟踪条。
        # HSV 的 OpenCV 量表为 H： 0-179， S： 0-255， V： 0-255
        cv.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)

        # 设置最大 HSV 跟踪条的默认值
        cv.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # 用于增加饱和度和值的跟踪栏
        cv.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

        # 根据控制 GUI 值返回 HSV 筛选器对象

    def get_hsv_filter_from_controls(self):
        hsv_filter = {
            "hMin": cv.getTrackbarPos('HMin', self.TRACKBAR_WINDOW),
            "sMin": cv.getTrackbarPos('SMin', self.TRACKBAR_WINDOW),
            "vMin": cv.getTrackbarPos('VMin', self.TRACKBAR_WINDOW),
            "hMax": cv.getTrackbarPos('HMax', self.TRACKBAR_WINDOW),
            "sMax": cv.getTrackbarPos('SMax', self.TRACKBAR_WINDOW),
            "vMax": cv.getTrackbarPos('VMax', self.TRACKBAR_WINDOW),
            "sAdd": cv.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW),
            "sSub": cv.getTrackbarPos('SSub', self.TRACKBAR_WINDOW),
            "vAdd": cv.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW),
            "vSub": cv.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        }
        return hsv_filter

    def undate_config(self, file):
        """
        :param file: 你保存的json文件名字
        :return:
        """
        with open(file, 'w') as js:
            json.dump(self.get_hsv_filter_from_controls(), js, indent='\t', ensure_ascii=False)

    def apply_hsv_filter(self, original_image, hsv_filter=None):
        # 将图像转换为 HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        # 如果我们没有被赋予定义的过滤器，请使用 GUI 中的过滤器值
        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        # 加减饱和度和值
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter['sAdd'])
        s = self.shift_channel(s, -hsv_filter['sSub'])
        v = self.shift_channel(v, hsv_filter['vAdd'])
        v = self.shift_channel(v, -hsv_filter['vSub'])
        hsv = cv.merge([h, s, v])

        # 设置要显示的最小和最大 HSV 值
        lower = np.array([hsv_filter['hMin'], hsv_filter['sMin'], hsv_filter['vMin']])
        upper = np.array([hsv_filter['hMax'], hsv_filter['sMax'], hsv_filter['vMax']])
        # 应用阈值
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # 转换回 BGR 以便 imshow（） 正确显示它
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img

    # 对 HSV 通道应用调整
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c


if __name__ == '__main__':
    from module import matching, windowCapture
    cap = windowCapture.WindowCapture((0, 31, 1027, 799))  # 截图类

    f = HsvFilter()
    f.init_control_gui()  # 初始化控制台
    while 1:
        screenshot = cap.screenshot()
        img = f.apply_hsv_filter(screenshot)
        cv.imshow('win', img)
        if cv.waitKey(1) == ord('q'):
            f.undate_config('HsvFilter.json')
            break
