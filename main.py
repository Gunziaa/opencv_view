from module import matching, windowCapture
from time import sleep

if __name__ == '__main__':
    cap = windowCapture.WindowCapture('剑网3 - 绝代天骄 @ 电信八区(点卡区)')
    matching = matching.Template(r'E:\Py\opencv_view\module\template.png')
    shap = matching.w, matching.h
    while True:
        screenshot = cap.get_screenshot()
        location = matching.matchingTemplate(screenshot)
        matching.show_rect(screenshot, location, shap)
        sleep(0.03)


