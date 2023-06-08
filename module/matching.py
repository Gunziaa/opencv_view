import json
from time import time, sleep

import cv2 as cv
import numpy as np


class Template:
    """匹配类"""
    threshold = 0  # 阈值
    tem = None  # 模板

    def __init__(self, tem):
        """
        :param tem:模板
        """
        self.tem = cv.imread(tem)  # 模板
        self.tem_size = self.tem.shape

    def matchingTemplate(self, src, threshold=0.7):
        """ 匹配模板
        src :主图
        """
        try:
            # 模板匹配
            result = cv.matchTemplate(src, self.tem, cv.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
            if maxVal > threshold:
                return maxLoc
        except cv.error:
            pass

    def show_rect(self, image, location, shape):
        """  显示图片
        :param image: 图片
        :param location: 矩形位置
        :param shape: 模板大小
        :return:
        """
        if location:
            x, y, x1, y1 = location[0], location[1], location[0] + shape[1], location[1] + shape[0]
            brcnt = np.array([[[x, y]], [[x1, y]], [[x1, y1]], [[x, y1]]])
            r = cv.drawContours(image, [brcnt], -1, (255, 10, 255), 2)
        else:
            r = image
        cv.imshow("result", r)


class HsvFilte:
    """颜色过滤"""

    def __init__(self, file):
        """
        :param file: json文件 hsv数据
        """
        self.hsv_filter = self.read_data(file)

    def read_data(self, file):
        with open(file) as js:
            config = json.load(js)
        return config

    def apply_hsv_filter(self, original_image):
        # 将图像转换为 HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)
        # 加减饱和度和值
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, self.hsv_filter['sAdd'])
        s = self.shift_channel(s, -self.hsv_filter['sSub'])
        v = self.shift_channel(v, self.hsv_filter['vAdd'])
        v = self.shift_channel(v, -self.hsv_filter['vSub'])
        hsv = cv.merge([h, s, v])

        # 设置要显示的最小和最大 HSV 值
        lower = np.array([self.hsv_filter['hMin'], self.hsv_filter['sMin'], self.hsv_filter['vMin']])
        upper = np.array([self.hsv_filter['hMax'], self.hsv_filter['sMax'], self.hsv_filter['vMax']])
        # 应用阈值
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # 转换回 BGR 以便 imshow（） 正确显示它
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)
        return img

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
    # 对 HSV 通道应用调整


if __name__ == '__main__':
    from module.windowCapture import WindowCapture

    cap = WindowCapture((0, 31, 1027, 799))
    temp = Template('xing1.png')
    co = HsvFilte('HsvFilter.json')

    loop_time = time()
    while True:
        screenshot = cap.screenshot()
        # screenshot = cv.cvtColor(screenshot, cv.COLOR_BGRA2BGR)
        screenshot1 = co.apply_hsv_filter(screenshot)
        location = temp.matchingTemplate(screenshot1)
        temp.show_rect(screenshot, location, temp.tem_size)

        print('FPS {} , 位置{}'.format(1 / (time() - loop_time), location))
        loop_time = time()
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break
        sleep(0.1)
