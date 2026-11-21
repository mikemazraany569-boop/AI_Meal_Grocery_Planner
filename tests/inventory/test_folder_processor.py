
from io import BytesIO

import pytest
from PIL import Image

from src.inventory.folder_processor import FolderProcessor


class MockUploadedFile(BytesIO):
    def __init__(self, name, content):
        super().__init__(content)
        self.name = name


def create_image(filename="tomato.jpg", image_format="JPEG"):
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (100, 100),
        color="red"
    )

    image.save(buffer, format=image_format)
    buffer.seek(0)

    return MockUploadedFile(filename, buffer.getvalue())


@pytest.fixture
def processor():
    return FolderProcessor()


def test_process_valid_jpeg(processor):
    uploaded = [create_image("tomato.jpg")]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 1
    assert result["total_files"] == 1
    assert result["skipped_files"] == []


def test_process_valid_png(processor):
    uploaded = [create_image("potato.png", "PNG")]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 1
    assert result["valid_images"][0]["format"] == "PNG"


def test_process_valid_webp(processor):
    uploaded = [create_image("onion.webp", "WEBP")]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 1
    assert result["valid_images"][0]["format"] == "WEBP"


def test_unsupported_extension_is_skipped(processor):
    uploaded = [
        MockUploadedFile("document.pdf", b"not an image")
    ]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 0
    assert len(result["skipped_files"]) == 1
    assert result["skipped_files"][0]["reason"] == (
        "Unsupported file format."
    )


def test_corrupted_image_is_skipped(processor):
    uploaded = [
        MockUploadedFile("corrupted.jpg", b"invalid image content")
    ]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 0
    assert len(result["skipped_files"]) == 1


def test_multiple_images_are_processed(processor):
    uploaded = [
        create_image("tomato.jpg"),
        create_image("potato.png", "PNG"),
        create_image("onion.webp", "WEBP"),
    ]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 3
    assert result["total_files"] == 3


def test_hidden_files_are_ignored(processor):
    uploaded = [
        create_image(".hidden.jpg")
    ]

    result = processor.process(uploaded)

    assert len(result["valid_images"]) == 0
    assert len(result["skipped_files"]) == 0
    assert result["total_files"] == 0


def test_empty_folder(processor):
    result = processor.process([])

    assert result["valid_images"] == []
    assert result["skipped_files"] == []
    assert result["total_files"] == 0


def test_none_input_raises_error(processor):
    with pytest.raises(ValueError):
        processor.process(None)


def test_image_dimensions_are_returned(processor):
    uploaded = [create_image("tomato.jpg")]

    result = processor.process(uploaded)

    image_data = result["valid_images"][0]

    assert image_data["width"] == 100
    assert image_data["height"] == 100


def test_filename_is_preserved(processor):
    uploaded = [create_image("ingredients/tomato.jpg")]

    result = processor.process(uploaded)

    assert result["valid_images"][0]["filename"] == (
        "ingredients/tomato.jpg"
    )
