
from pathlib import Path
from PIL import Image, UnidentifiedImageError


class FolderProcessor:
    """Validate and prepare ingredient images uploaded as a folder."""

    SUPPORTED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    def process(self, uploaded_files):
        """
        Process uploaded files and return valid images.

        Parameters
        ----------
        uploaded_files : iterable
            Uploaded file objects exposing name and read().

        Returns
        -------
        dict
            valid_images, skipped_files, total_files
        """
        if uploaded_files is None:
            raise ValueError("Uploaded files cannot be None.")

        valid_images = []
        skipped_files = []

        for uploaded_file in uploaded_files:
            filename = getattr(uploaded_file, "name", None)

            if not filename:
                skipped_files.append({
                    "filename": "Unknown",
                    "reason": "Missing filename."
                })
                continue

            path = Path(filename)

            # Ignore hidden files and directories.
            if any(part.startswith(".") for part in path.parts):
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                skipped_files.append({
                    "filename": filename,
                    "reason": "Unsupported file format."
                })
                continue

            try:
                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
                image.verify()

                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
                image.load()

                if image.width <= 0 or image.height <= 0:
                    raise ValueError("Invalid image dimensions.")

                valid_images.append({
                    "filename": filename,
                    "image": image.copy(),
                    "format": image.format,
                    "width": image.width,
                    "height": image.height,
                })

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as error:
                skipped_files.append({
                    "filename": filename,
                    "reason": f"Invalid or corrupted image: {error}"
                })

        return {
            "valid_images": valid_images,
            "skipped_files": skipped_files,
            "total_files": len(valid_images) + len(skipped_files),
        }
