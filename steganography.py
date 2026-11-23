
from stegano import lsb
from io import BytesIO
from PIL import Image


def hide_message(image_bytes, message):

    if not image_bytes or not message:
        raise ValueError(
            "Gambar dan pesan wajib diisi."
        )

    try:
        img = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        # Sembunyikan pesan menggunakan LSB
        output = lsb.hide(img, message)

        # Simpan hasil menjadi PNG
        buffer = BytesIO()

        output.save(
            buffer,
            format="PNG"
        )

        return buffer.getvalue()

    except Exception as e:
        raise ValueError(
            f"Gagal menyembunyikan pesan: {e}"
        ) from e


def reveal_message(image_bytes):

    if not image_bytes:
        raise ValueError("Gambar wajib diunggah.")

    try:
        img = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        message = lsb.reveal(img)

        if message is None:
            raise ValueError(
                "Tidak ditemukan pesan tersembunyi."
            )

        return message

    except Exception as e:
        raise ValueError(
            f"Gagal membaca pesan: {e}"
        ) from e
