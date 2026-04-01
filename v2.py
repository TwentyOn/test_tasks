"""
Мониторинг столика: детекция событий через YOLOv8 + OpenCV
Зависимости: pip install ultralytics opencv-python
"""

import cv2
import time
from collections import deque
from ultralytics import YOLO

# ─── Настройки ────────────────────────────────────────────────────────────────
VIDEO_SOURCE = 'видео 2.mp4'          # 0 = веб-камера, или путь к файлу: "video.mp4"
CONF_THRESHOLD = 0.4      # минимальная уверенность детекции человека
# Сколько секунд без людей считать "столик пуст" (дебаунс)
EMPTY_DEBOUNCE_SEC = 3.0
# Сколько кадров усреднять для сглаживания (убирает мигание)
SMOOTHING_FRAMES = 10
# ──────────────────────────────────────────────────────────────────────────────

LOG_FILE = "table_events.log"

def log_event(event: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {event}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def select_roi(cap) -> tuple[int, int, int, int]:
    """Показать первый кадр и дать пользователю выбрать зону столика."""
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Не удалось прочитать первый кадр видео.")
    print("Выберите зону столика мышью, затем нажмите ENTER или SPACE.")
    roi = cv2.selectROI("Выберите зону столика", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Выберите зону столика")
    x, y, w, h = roi
    if w == 0 or h == 0:
        raise ValueError("Зона не выбрана. Запустите снова.")
    return x, y, w, h


def people_in_zone(results, zone: tuple[int, int, int, int]) -> int:
    """Считает людей (class 0 = person), чей центр находится внутри зоны."""
    zx, zy, zw, zh = zone
    count = 0
    for box in results[0].boxes:
        cls = int(box.cls[0])
        if cls != 0:  # только люди
            continue
        conf = float(box.conf[0])
        if conf < CONF_THRESHOLD:
            continue
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if zx <= cx <= zx + zw and zy <= cy <= zy + zh:
            count += 1
    return count


def draw_overlay(frame, zone, state: str, count: int):
    zx, zy, zw, zh = zone
    color = {
        "EMPTY":    (100, 100, 100),
        "OCCUPIED": (50, 200, 50),
        "APPROACH": (50, 100, 255),
    }.get(state, (255, 255, 255))

    cv2.rectangle(frame, (zx, zy), (zx + zw, zy + zh), color, 2)

    label = {
        "EMPTY":    "Пусто",
        "OCCUPIED": f"Занято ({count} чел.)",
        "APPROACH": "⚡ Подход!",
    }.get(state, state)

    cv2.rectangle(frame, (zx, zy - 28), (zx + zw, zy), color, -1)
    cv2.putText(frame, label, (zx + 4, zy - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    return frame


def main():
    model = YOLO("yolov8n.pt")   # скачается автоматически при первом запуске
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть источник: {VIDEO_SOURCE}")

    zone = select_roi(cap)
    print(f"Зона столика: x={zone[0]}, y={zone[1]}, w={zone[2]}, h={zone[3]}")
    log_event("=== Мониторинг запущен ===")

    # Скользящее окно для сглаживания количества людей
    window: deque[int] = deque(maxlen=SMOOTHING_FRAMES)

    state = "EMPTY"           # текущее состояние
    empty_since: float = 0.0  # timestamp когда зона опустела
    near_since: float = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        raw_count = people_in_zone(results, zone)
        window.append(raw_count)
        smooth_count = round(sum(window) / len(window))

        # ─── Конечный автомат состояний ─────────────────────────────────────
        if smooth_count > 0:
            if state == "EMPTY":
                # Появился человек — фиксируем "Подход"
                state = "APPROACH"
                near_since = time.time()
                log_event(f"ПОДХОД К СТОЛИКУ (людей: {smooth_count})")
            elif state == "APPROACH":
                if time.time() - near_since >= 2:
                    near_since = 0.0
                    # Через один проход переходим в "Занято"
                    state = "OCCUPIED"
                    log_event(f"СТОЛ ЗАНЯТ (людей: {smooth_count})")
            # В состоянии OCCUPIED просто обновляем счётчик
            empty_since = 0.0
        else:
            if state in ("OCCUPIED", "APPROACH"):
                if empty_since == 0.0:
                    empty_since = time.time()
                elif time.time() - empty_since >= EMPTY_DEBOUNCE_SEC:
                    state = "EMPTY"
                    log_event("СТОЛ ПУСТОЙ")
                    empty_since = 0.0
            # Уже EMPTY — ничего не делаем
        # ────────────────────────────────────────────────────────────────────

        frame = draw_overlay(frame, zone, state, smooth_count)
        cv2.imshow("Table Monitor  [Q - выход]", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    log_event("=== Мониторинг остановлен ===")
    print(f"\nСобытия сохранены в: {LOG_FILE}")


if __name__ == "__main__":
    main()