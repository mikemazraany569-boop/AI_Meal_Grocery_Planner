
from io import BytesIO
from unittest.mock import Mock

import pytest
from PIL import Image

from src.vision.folder_ingredient_detector import (
    FolderIngredientDetector,
)


class MockUploadedFile(BytesIO):
    def __init__(self, name, content):
        super().__init__(content)
        self.name = name


def create_image(filename, image_format="JPEG"):
    buffer = BytesIO()

    image = Image.new("RGB", (100, 100), color="red")
    image.save(buffer, format=image_format)

    buffer.seek(0)

    return MockUploadedFile(
        filename,
        buffer.getvalue(),
    )


@pytest.fixture
def mock_ingredient_detector():
    detector = Mock()
    detector.detect.return_value = [
        {
            "label": "tomato",
            "confidence": 0.95,
            "box": [10, 20, 50, 60],
        }
    ]
    return detector


@pytest.fixture
def folder_detector(mock_ingredient_detector):
    return FolderIngredientDetector(
        ingredient_detector=mock_ingredient_detector
    )


def test_process_single_image(folder_detector):
    uploaded = [create_image("tomato.jpg")]

    result = folder_detector.process(uploaded)

    assert result["total_images"] == 1
    assert result["successful_images"] == 1
    assert len(result["per_image"]) == 1
    assert len(result["ingredients"]) == 1
    assert result["ingredients"][0]["label"] == "tomato"


def test_process_multiple_images(
    folder_detector,
    mock_ingredient_detector,
):
    uploaded = [
        create_image("tomato.jpg"),
        create_image("potato.png", "PNG"),
        create_image("onion.webp", "WEBP"),
    ]

    result = folder_detector.process(uploaded)

    assert result["total_images"] == 3
    assert result["successful_images"] == 3
    assert mock_ingredient_detector.detect.call_count == 3


def test_duplicate_ingredients_are_aggregated(
    folder_detector,
):
    uploaded = [
        create_image("photo1.jpg"),
        create_image("photo2.jpg"),
    ]

    result = folder_detector.process(uploaded)

    assert len(result["ingredients"]) == 1

    tomato = result["ingredients"][0]

    assert tomato["label"] == "tomato"
    assert tomato["detection_count"] == 2
    assert tomato["image_count"] == 2


def test_aggregation_preserves_confidence_scores(
    folder_detector,
    mock_ingredient_detector,
):
    mock_ingredient_detector.detect.side_effect = [
        [
            {
                "label": "tomato",
                "confidence": 0.95,
                "box": [10, 20, 50, 60],
            }
        ],
        [
            {
                "label": "tomato",
                "confidence": 0.85,
                "box": [15, 25, 55, 65],
            }
        ],
    ]

    uploaded = [
        create_image("photo1.jpg"),
        create_image("photo2.jpg"),
    ]

    result = folder_detector.process(uploaded)

    tomato = result["ingredients"][0]

    assert tomato["max_confidence"] == 0.95
    assert tomato["average_confidence"] == 0.90


def test_images_without_detections(
    folder_detector,
    mock_ingredient_detector,
):
    mock_ingredient_detector.detect.return_value = []

    uploaded = [create_image("empty.jpg")]

    result = folder_detector.process(uploaded)

    assert result["successful_images"] == 1
    assert result["per_image"][0]["detections"] == []
    assert result["ingredients"] == []


def test_invalid_confidence_values(folder_detector):
    invalid_values = [
        0,
        -0.1,
        1.1,
        "0.5",
        None,
        True,
    ]

    for confidence in invalid_values:
        with pytest.raises(ValueError):
            folder_detector.process(
                [create_image("tomato.jpg")],
                confidence=confidence,
            )


def test_valid_confidence_is_forwarded(
    folder_detector,
    mock_ingredient_detector,
):
    folder_detector.process(
        [create_image("tomato.jpg")],
        confidence=0.65,
    )

    args, kwargs = mock_ingredient_detector.detect.call_args

    assert kwargs["confidence"] == 0.65


def test_skipped_files_are_returned(folder_detector):
    uploaded = [
        create_image("tomato.jpg"),
        MockUploadedFile("document.pdf", b"not an image"),
    ]

    result = folder_detector.process(uploaded)

    assert result["total_files"] == 2
    assert result["total_images"] == 1
    assert result["successful_images"] == 1
    assert len(result["skipped_files"]) == 1


def test_detection_observations_include_filename(
    folder_detector,
):
    uploaded = [create_image("tomatoes.jpg")]

    result = folder_detector.process(uploaded)

    observation = result["ingredients"][0]["observations"][0]

    assert observation["filename"] == "tomatoes.jpg"
    assert observation["confidence"] == 0.95


def test_per_image_results_preserve_filename(
    folder_detector,
):
    uploaded = [create_image("ingredients/tomato.jpg")]

    result = folder_detector.process(uploaded)

    assert result["per_image"][0]["filename"] == (
        "ingredients/tomato.jpg"
    )


def test_empty_folder(folder_detector):
    result = folder_detector.process([])

    assert result["total_images"] == 0
    assert result["successful_images"] == 0
    assert result["ingredients"] == []
    assert result["per_image"] == []


def test_detected_ingredients_are_sorted(folder_detector):
    mock_detector = Mock()

    mock_detector.detect.return_value = [
        {
            "label": "tomato",
            "confidence": 0.95,
            "box": [10, 20, 50, 60],
        },
        {
            "label": "apple",
            "confidence": 0.90,
            "box": [20, 30, 60, 70],
        },
    ]

    detector = FolderIngredientDetector(
        ingredient_detector=mock_detector
    )

    result = detector.process([
        create_image("ingredients.jpg")
    ])

    labels = [
        item["label"]
        for item in result["ingredients"]
    ]

    assert labels == ["apple", "tomato"]


def test_temporary_image_is_passed_to_detector(
    folder_detector,
    mock_ingredient_detector,
):
    folder_detector.process([
        create_image("tomato.jpg")
    ])

    args, kwargs = mock_ingredient_detector.detect.call_args

    image_path = args[0]

    assert image_path.exists() is False
    assert image_path.name == "image_1.jpg"
