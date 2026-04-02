import os.path
import time
import argparse
import tkinter
import logging
from distutils.util import strtobool
from collections import deque

import cv2
import numpy as np
from ultralytics import YOLO
import pandas as pd

logging.basicConfig(level=logging.DEBUG, format='[{asctime}] #{levelname:4} - {message}', style='{')
logger = logging.getLogger(__name__)

# клиентские размеры экрана
SCREEN_WIDTH, SCREEN_HEIGHT = tkinter.Tk().winfo_screenwidth(), tkinter.Tk().winfo_screenheight()


class EventRecorder:
    """
    Запись событий и рачет средней задержки
    """

    def __init__(self):
        self.events_df = pd.DataFrame(columns=['event', 'timestamp'])

        self.event = {
            'EMPTY': 'столик освободился',
            'OCCUPIED': 'столик занят'
        }

    def log_event(self, event: str):
        """
        Записать событие в датафрейм
        :param event:
        :return:
        """
        ts = time.time()
        cur_index = len(self.events_df)
        self.events_df.loc[cur_index] = {
            'event': event,
            'timestamp': ts
        }
        logger.debug(f'зафиксировано событие: {event}')
        self.calc_avg_empty()

    def calc_avg_empty(self):
        """
        Расчет средней задержки
        :return:
        """
        result = []

        empty_ev_df = self.events_df[self.events_df['event'] == self.event['EMPTY']]

        for i in empty_ev_df.index.tolist():
            start_time = empty_ev_df.loc[i, 'timestamp']

            occupied_ev_df = self.events_df.loc[i + 1:]
            occupied_ev_df = occupied_ev_df[occupied_ev_df['event'] == self.event['OCCUPIED']]
            if not occupied_ev_df.empty:
                end_time = occupied_ev_df.iloc[0]['timestamp']
                result.append(end_time - start_time)

        if result:
            return np.array(result).mean()

    def write_to_csv(self):
        """
        Вывод всех событий в файл
        :return:
        """
        self.events_df.to_csv('logs.csv')


class TableMonitor:
    """
    Мониторинг зоны интереса на видео
    """

    def __init__(self, filename: str, event_recorder: EventRecorder, headless: bool):
        self.headless = headless

        self.cap = cv2.VideoCapture(filename)
        self.model = YOLO('yolov8n.pt')
        self.event_recorder = event_recorder

        self.video_writer = None

        # координаты выбранной зона интереса
        self.roi = None

        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        # время на смену состояния
        self.DEBOUNCE_SEC = 3.0

        self.window: deque[int] = deque(maxlen=self.fps * int(self.DEBOUNCE_SEC))

        # уровень уверенности модели
        self.CONF_THRESHOLD = 0.4

        # начальное состояние
        self.state = 'EMPTY'

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

    def state_machine(self) -> None:
        """
        Модель конечного автомата для изменения состояний
        :return:
        """
        if sum(self.window):
            if self.state == 'EMPTY':
                self.event_recorder.log_event('человек у столика')
                self.state = 'APPROACH'
            elif self.state == 'APPROACH':
                if sum(self.window) == self.fps * self.DEBOUNCE_SEC:
                    self.event_recorder.log_event('столик занят')
                    self.state = 'OCCUPIED'
        else:
            if self.state == 'APPROACH':
                self.state = 'EMPTY'
            elif self.state == 'OCCUPIED':
                self.event_recorder.log_event('столик освободился')
                self.state = 'EMPTY'

    def run(self):
        """
        Главный цикл обработки
        :return:
        """
        # объект для записи выходного видеофайла
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter('output.mp4', fourcc, self.fps, (width, height))

        self.roi = self.get_roi_area()
        while True:
            ret, frame = self.cap.read()

            if not ret:
                self.event_recorder.write_to_csv()

                avg_delay = self.event_recorder.calc_avg_empty()
                logger.info(f'всего событий зарегистировано: {len(self.event_recorder.events_df)}')
                logger.info(f'cреднее время между уходом гостя и подходом следующего человека: {avg_delay}c')

                cv2.destroyAllWindows()
                self.video_writer.release()

                break

            detections = self.detect_pople(frame)
            has_people = self.table_occupied(detections)
            self.window.append(has_people)
            self.state_machine(has_people)

            # if detections:
            #     for item in detections:
            #         x1, y1, x2, y2 = [int(i) for i in item]
            #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            self.draw_overlay(frame)

            if self.video_writer:
                self.video_writer.write(frame)

            if not self.headless:
                cv2.imshow('monitor', frame)
                cv2.resizeWindow('monitor', SCREEN_WIDTH, SCREEN_HEIGHT)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                avg_delay = self.event_recorder.calc_avg_empty()
                logger.info(f'всего событий зарегистировано: {len(self.event_recorder.events_df)}')
                logger.info(f'cреднее время между уходом гостя и подходом следующего человека: {avg_delay}c')

                self.cap.release()
                self.video_writer.release()
                cv2.destroyAllWindows()
                break


def main():
    # аргументы командной строки
    parser = argparse.ArgumentParser(description='детектор событий для зоны интереса')
    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='путь к видеофайлу'
    )
    parser.add_argument(
        '--headless',
        default=True,
        type=lambda x: bool(strtobool(x)),
        help='отображать окно с видеофайлом'
    )

    args = parser.parse_args()
    filename: str = args.video

    # отображать или нет окно обработки видео
    headless: bool = args.headless

    # валидация имени файла
    if not filename.endswith('.mp4'):
        raise ValueError('неподдерживаемый формат видеофайла. (только mp4)')
    elif not os.path.exists(filename):
        raise ValueError(f'файл не найден: {filename}')

    # объект для записи событий
    recorder = EventRecorder()

    # основная программа для детекции движения
    monitor = TableMonitor(filename, recorder, headless)
    monitor.run()


if __name__ == '__main__':
    main()
