import os
from importlib.resources import files
from pathlib import Path


def get_installation_dir() -> Path:
    installation_path = Path(__file__).resolve().parent.parent.parent
    return installation_path


def get_character_template_location() -> Path:
    template_dir = Path(
        os.getenv(
            "USCM_TEMPLATE_DIR",
            default=files("uscm_character_generator").joinpath("templates"),
        )
    )
    return template_dir


def get_character_save_location() -> Path:
    character_save_dir = Path(
        os.getenv(
            "USCM_CHARACTER_DIR",
            default=get_installation_dir().joinpath("local_characters"),
        )
    )
    return character_save_dir


def get_pdf_save_location() -> Path:
    pdf_save_dir = Path(
        os.getenv(
            "USCM_PDF_DIR", default=get_installation_dir().joinpath("local_characters")
        )
    )
    return pdf_save_dir


def get_character_template() -> Path:
    template = get_character_template_location().joinpath("template.json")
    return template
