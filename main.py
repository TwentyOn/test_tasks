import cv2
from ultralytics import YOLO


class TableMonitor:
    def __init__(self):
        self.cap = cv2.VideoCapture('видео 2.mp4')
        self.model = YOLO('yolov8n.pt')
        self.roi = None
        self.DEBOUNCE_SEC = 3.0
        self.SMOOTHING_FRAMES = 10
        self.CONF_THRESHOLD = 0.4

    def get_roi_area(self):
        ret, frame = self.cap.read()

        if not ret:
            return

        roi = cv2.selectROI(windowName='get insterest table', img=frame, showCrosshair=False, fromCenter=False)
        cv2.destroyWindow('get insterest table')
        return roi

    def table_occupied(self, detections):
        x1_1, y1_1, x2_1, y2_1 = self.roi
        x2_1 += x1_1
        y2_1 += y1_1
        table_area = x2_1 * y2_1

        for det in detections:
            # Координаты bounding box человека
            x1_2, y1_2, x2_2, y2_2 = det
            person_area = (x2_2 - x1_2) * (y2_2 - y1_2)

            # Вычисляем пересечение с зоной столика
            if x2_1 < x1_2 or x2_2 < x1_1 or y2_1 < y1_2 or y2_2 < y1_1:
                continue
            else:
                return True

        return False

    def detect_pople(self, frame):
        detections = []

        result = self.model(frame, conf=self.CONF_THRESHOLD)[0]
        boxes = result.boxes

        for box in boxes:
            x, y, w, h = box.xyxy[0].cpu().numpy()
            cls = int(box.cls[0])

            if cls == 0:
                detections.append([x, y, w, h])

        return detections

    def draw_overlay(self, frame, state):
        x, y, w, h = self.roi
        color = {
            'EMPTY': (100, 100, 100),
            'OCCUPIED': (0, 0, 255),
            'APPROACH': (50, 100, 255)
        }.get(state, (255, 255, 255))

        cv2.rectangle(frame, (x, y), (x + w, y + h), 2)

        label = {
            'EMPTY': 'empty',
            'OCCUPIED': 'occupied',
            'APPROACH': 'approach',
        }.get(state, state)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f'status: {label}', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1)

    def run(self):
        self.roi = self.get_roi_area()
        if not self.roi:
            raise IOError('столик не выбран, повторите попытку')

        while True:
            ret, frame = self.cap.read()

            if not ret:
                raise IOError('не удалось открыть видеофайл')

            detections = self.detect_pople(frame)

            is_occupied = self.table_occupied(detections)
            x, y, w, h = self.roi
            if detections:
                for item in detections:
                    x1, y1, x2, y2 = [int(i) for i in item]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if is_occupied:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.draw_overlay(frame, 'EMPTY' if not is_occupied else 'OCCUPIED')

            cv2.imshow('monitor', frame)
            cv2.resizeWindow('monitor', 1920, 1080)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break


monitor = TableMonitor()
monitor.run()
