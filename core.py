"""Recompte de persones. No conté telemetria ni resultats de demostració."""
import csv
import io
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps


def prepare_image(image):
    image = ImageOps.exif_transpose(image).convert('RGB')
    image.thumbnail((1600, 1600))
    return image


def detect_people(model, image, confidence=0.35):
    result = model.predict(source=image, classes=[0], conf=confidence, iou=0.5,
                           imgsz=960, device='cpu', verbose=False)[0]
    detections = []
    if result.boxes is not None:
        for box in result.boxes:
            detections.append({'box': box.xyxy[0].cpu().tolist(),
                               'confidence': float(box.conf[0].cpu())})
    return detections


def annotate(image, detections):
    marked = image.copy()
    draw = ImageDraw.Draw(marked)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    for number, det in enumerate(detections, 1):
        x1, y1, x2, y2 = det['box']
        draw.rectangle((x1, y1, x2, y2), outline='#16a085', width=3)
        text = f"{number} | {det['confidence']:.0%}"
        y = max(0, y1 - 24)
        rect = draw.textbbox((x1, y), text, font=font)
        draw.rectangle(rect, fill='#075e50')
        draw.text((x1, y), text, fill='white', font=font)
    return marked


def image_bytes(image, fmt='PNG'):
    out = io.BytesIO()
    image.save(out, format=fmt)
    return out.getvalue()


def analyse_video(path, detector, sample_fps=8, max_seconds=10, progress=None):
    import cv2
    cap = cv2.VideoCapture(str(path))
    frames = []
    try:
        if not cap.isOpened():
            raise ValueError('No es pot obrir el vídeo. Prova un MP4 amb còdec H.264.')
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError('El vídeo no té una freqüència de fotogrames vàlida.')
        declared = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if math.isfinite(declared) and declared > 0 and declared / fps > max_seconds + 1 / fps:
            raise ValueError(f'El vídeo supera els {max_seconds} segons. Retalla’l abans de carregar-lo.')
        index, next_time = 0, 0.0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            timestamp = index / fps
            if timestamp >= max_seconds:
                raise ValueError(f'El vídeo supera els {max_seconds} segons.')
            if timestamp + 1e-9 >= next_time:
                image = prepare_image(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                detections = detector(image)
                frames.append({'second': round(timestamp, 3), 'count': len(detections),
                               'image': image_bytes(annotate(image, detections), 'JPEG')})
                next_time += 1 / sample_fps
                if progress:
                    progress(min(0.99, (index + 1) / declared if declared > 0 else timestamp / max_seconds))
            index += 1
        if not frames:
            raise ValueError('No s’ha pogut llegir cap fotograma.')
        if progress:
            progress(1.0)
        return {'frames': frames, 'duration': index / fps,
                'maximum': max(f['count'] for f in frames),
                'peak_index': max(range(len(frames)), key=lambda i: frames[i]['count'])}
    finally:
        cap.release()


def export_csv(name, kind, rows, automatic, corrected):
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['fitxer', 'tipus', 'segon', 'persones_detectades',
                     'recompte_automatic', 'recompte_revisat'])
    for row in rows:
        writer.writerow([name, kind, row.get('second', ''), row['count'], automatic, corrected])
    return ('\ufeff' + output.getvalue()).encode('utf-8')
