import cv2
import numpy as np

def cv2_detection():
    cap = cv2.VideoCapture('видео 2.mp4')
    backSub = cv2.createBackgroundSubtractorKNN()
    if not cap.isOpened():
        print('aboba')
    else:
        ret, frame = cap.read()
        roi = cv2.selectROI(windowName='kkk', img=frame, showCrosshair=True, fromCenter=False)
        cv2.destroyWindow('kkk')
        print(roi)
        while cap.isOpened():
            # Захват кадр за кадром
            ret, frame = cap.read()

            if ret:
                # Вычитание фона
                fg_mask = backSub.apply(frame)

                # устанавливаем глобальный порог для удаления теней
                retval, mask_thresh = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)

                # вычисление ядра
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                # Apply erosion
                mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)
                x, y, w, h = roi
                roi_mask = fg_mask[y:y + h, x: x + w]
                moving = np.sum(roi_mask > 0)
                roi_area = w * h

                print(moving / roi_area)
                print(moving / roi_area > 0.05)

                # Поиск контура
                contours, hierarchy = cv2.findContours(mask_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                min_contour_area = 3000  # Define your minimum area threshold
                large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
                frame_ct = cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
                frame_out = frame.copy()
                if moving / roi_area > 0.05:
                    cv2.rectangle(frame_out, (x, y), (x + w, y + h), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame_out, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # отображаем результат
                cv2.imshow('test', frame_out)
                cv2.resizeWindow('test', 1440, 900)

                # показать итоговый кадр
                # cv2.imshow('test', frame_ct)
                # cv2.resizeWindow('test', 1440, 900)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

cv2_detection()