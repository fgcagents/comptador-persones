import io
import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from core import analyse_video, annotate, export_csv, image_bytes, prepare_image

class CoreTests(unittest.TestCase):
    def video(self, directory, seconds=1, fps=12):
        path = str(Path(directory) / 'test.avi')
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), fps, (64, 64))
        for i in range(seconds * fps):
            writer.write(np.full((64, 64, 3), i, dtype=np.uint8))
        writer.release()
        return path

    def test_video_maximum_not_sum(self):
        with tempfile.TemporaryDirectory() as d:
            counts = iter([1, 3, 2, 1])
            result = analyse_video(self.video(d), lambda _: [{'box': [1, 1, 20, 30], 'confidence': .8}] * next(counts), sample_fps=4)
        self.assertEqual([f['count'] for f in result['frames']], [1, 3, 2, 1])
        self.assertEqual(result['maximum'], 3)
        self.assertEqual(result['peak_index'], 1)
        self.assertAlmostEqual(result['duration'], 1)

    def test_empty_scene(self):
        with tempfile.TemporaryDirectory() as d:
            result = analyse_video(self.video(d), lambda _: [], sample_fps=2)
        self.assertEqual(result['maximum'], 0)

    def test_invalid_video_and_duration(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                analyse_video(str(Path(d)/'missing.mp4'), lambda _: [])
            with self.assertRaises(ValueError):
                analyse_video(self.video(d, seconds=2), lambda _: [], max_seconds=1)

    def test_model_failure_is_not_a_fake_count(self):
        def failure(_):
            raise RuntimeError('model failed')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                analyse_video(self.video(d), failure)

    def test_export_and_annotation(self):
        csv = export_csv('foto.png', 'foto', [{'count': 2}], 2, 3).decode('utf-8-sig')
        self.assertIn('foto.png;foto;;2;2;3', csv)
        image = prepare_image(Image.new('RGB', (2000, 1000), 'white'))
        self.assertEqual(image.size, (1600, 800))
        data = image_bytes(annotate(image, [{'box': [10, 10, 100, 200], 'confidence': .9}]))
        self.assertEqual(Image.open(io.BytesIO(data)).size, (1600, 800))

if __name__ == '__main__':
    unittest.main()
