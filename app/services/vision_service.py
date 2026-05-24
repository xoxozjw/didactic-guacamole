from __future__ import annotations

from google.cloud import vision


def ocr_image(image_bytes: bytes) -> str:
    """對圖像執行 OCR，回傳辨識出的文字。"""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    if response.error.message:
        raise RuntimeError(response.error.message)
    annotations = response.text_annotations
    return annotations[0].description if annotations else ""
