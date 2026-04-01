import time

import cv2
from ultralytics import YOLO

LOG_FILE = "table_events.log"


def log_event(event: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {event}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class TableMonitor:
    def __init__(self):
        self.cap = cv2.VideoCapture('видео 2.mp4')
        self.model = YOLO('yolov8n.pt')
        self.roi = None
        self.DEBOUNCE_SEC = 5.0
        self.SMOOTHING_FRAMES = 10
        self.CONF_THRESHOLD = 0.4
        self.state = 'EMPTY'
        self.last_time = 0.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter('test.mp4', fourcc, 15.0, (1920, 1080))

    def get_roi_area(self) -> tuple[int]:
        """
        Получить зону интереса (столика)
        :return:
        """
        ret, frame = self.cap.read()

        if not ret:
            raise IOError('не удалось открыть видео')

        x, y, w, h = cv2.selectROI(
            windowName='get insterest table',
            img=frame,
            showCrosshair=False,
            fromCenter=False
        )

        if w == 0 or h == 0:
            raise IOError('столик не выбран, повторите попытку')

        cv2.destroyWindow('get insterest table')
        return x, y, w, h

    def table_occupied(self, detections: list[list[int]]) -> bool:
        """
        Проверяет наличие людей в зоне столика
        :param detections: bounding box человека
        :return: true - есть людди / false - нет людей
        """
        x1_1, y1_1, x2_1, y2_1 = self.roi
        x2_1 += x1_1
        y2_1 += y1_1

        for det in detections:
            x1_2, y1_2, x2_2, y2_2 = det

            # координаты центра bounding box
            cx, cy = (x1_2 + x2_2) / 2, (y1_2 + y2_2) / 2

            # человек в зоне только если его центр в зоне
            if x1_1 <= cx <= x1_1 + x2_1 and y1_1 <= cy <= y1_1 + y2_1:
                return True
            else:
                continue

        return False

    def detect_pople(self, frame):
        detections = []

        result = self.model(frame, conf=self.CONF_THRESHOLD, verbose=False)[0]
        boxes = result.boxes

        # находим координаты bounding box только для людей
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cls = int(box.cls[0])

            if cls == 0:
                detections.append([x1, y1, x2, y2])

        return detections

    def draw_overlay(self, frame) -> None:
        """
        Рисование рамки для выбранной зоны в зависимости от наличия людей
        :param frame: кадр
        :return:
        """
        x, y, w, h = self.roi
        color = {
            'EMPTY': (100, 100, 100),
            'OCCUPIED': (0, 0, 255),
            'APPROACH': (50, 100, 255)
        }.get(self.state, (255, 255, 255))

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        label = {
            'EMPTY': 'empty',
            'OCCUPIED': 'occupied',
            'APPROACH': 'approach',
        }.get(self.state, self.state)
        cv2.putText(
            frame,
            f'status: {label}',
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )

    def state_machine(self, has_people: bool) -> None:
        """
        Модель конечного автомата для изменения состояний
        :param has_people:
        :return:
        """
        if has_people:
            if self.state == 'EMPTY':
                log_event('кто-то подошел к столику')
                self.last_time = time.time()
                self.state = 'APPROACH'
            elif self.state == 'APPROACH':
                if time.time() - self.last_time >= self.DEBOUNCE_SEC:
                    log_event('столик заняли')
                    self.last_time = 0.0
                    self.state = 'OCCUPIED'
            else:
                self.last_time = 0.0
        else:
            if self.state in ('APPROACH', 'OCCUPIED'):
                if self.last_time == 0.0:
                    self.last_time = time.time()
                elif time.time() - self.last_time >= self.DEBOUNCE_SEC:
                    log_event('столик освободился')
                    self.state = 'EMPTY'
                    self.last_time = 0.0

    def run(self):
        """
        Главный цикл
        :return:
        """
        self.roi = self.get_roi_area()

        while True:
            ret, frame = self.cap.read()

            if not ret:
                break

            detections = self.detect_pople(frame)
            has_people = self.table_occupied(detections)
            self.state_machine(has_people)

            # if detections:
            #     for item in detections:
            #         x1, y1, x2, y2 = [int(i) for i in item]
            #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            self.draw_overlay(frame)

            if self.video_writer is not None:
                self.video_writer.write(frame)

            cv2.imshow('monitor', frame)
            cv2.resizeWindow('monitor', 1440, 900)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                self.cap.release()
                self.video_writer.release()
                cv2.destroyAllWindows()
                break


monitor = TableMonitor()
monitor.run()
