import cv2 as cv
import numpy as np


class Template:
    """匹配类"""
    threshold = 0  # 阈值
    tem = None  # 模板

    def __init__(self, tem):
        self.tem = cv.imread(tem)  # 模板
        self.h, self.w, ar = self.tem.shape

    def matchingTemplate(self, src, threshold=0.7):
        """ 匹配模板

        :param tem: 模板,图片读取后的数据 ( cv2.imread(obj, 0) )
        :param threshold: 阈值,调整匹配相似度
        :return: 模板位置
        """
        # 读取灰度模板
        # src = cv2.imread(obj, cv2.IMREAD_GRAYSCALE)
        # 模板二值化
        # retval, dst = cv2.threshold(src, 130, 255, cv2.THRESH_BINARY)
        try:
            # 模板匹配
            result = cv.matchTemplate(src, self.tem, cv.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)

            # 判断成功率阈值
            # print(minVal, maxVal, minLoc, maxLoc)
            # # if maxVal > threshold:
            #     print(maxLoc)
            return maxLoc

        except cv.error:
            pass


    def show_rect(self, image, location, shape):
        """
        :param image: 图片
        :param location: 矩形位置
        :param shape: 模板大小
        :return:
        """
        x, y, x1, y1 = location[0], location[1], location[0] + shape[0], location[1] + shape[1]
        brcnt = np.array([[[x, y]], [[x1, y]], [[x1, y1]], [[x, y1]]])
        r = cv.drawContours(image, [brcnt], -1, (255, 10, 255), 2)
        cv.imshow("result", r)
        cv.waitKey(10)
