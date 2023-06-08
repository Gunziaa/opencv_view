from module import matching, windowCapture, hsvfilter
from time import time, sleep
import cv2 as cv

if __name__ == '__main__':
    cap = windowCapture.WindowCapture((0, 31, 1027, 799))
    mat = matching.Template(r'E:\Py\opencv_view\module\xing1.png')
    f = matching.HsvFilte('E:\Py\opencv_view\module\HsvFilter.json')
    loop_time = time()
    while True:
        screenshot = cap.screenshot()
        srceenshot = cv.cvtColor(screenshot, cv.COLOR_BGRA2BGR)
        img = f.apply_hsv_filter(srceenshot)

        location = mat.matchingTemplate(img)  # 匹配
        mat.show_rect(screenshot, location, mat.tem_size)

        print('FPS {} , 位置{}'.format(1 / (time() - loop_time), location))
        loop_time = time()
        sleep(0.1)
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break
