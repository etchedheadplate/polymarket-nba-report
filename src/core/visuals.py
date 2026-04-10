import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from matplotlib import font_manager as fm
from PIL import Image

from src.config import settings
from src.logger import logger


class Visuals(ABC):
    _img_params: dict[str, Any]
    _img_path_background: Path | None
    _img_ext_transparent: str = "png"
    _img_ext_composed: str = "jpg"

    def __init__(self, visuals_title: str, query: Any, dataset: Any) -> None:
        self._visuals_dir = settings.OUTPUT_DIR / visuals_title
        self._query = query
        self._dataset = dataset
        os.makedirs(self._visuals_dir, exist_ok=True)

        if settings.FONT_PATH:
            try:
                fm.fontManager.addfont(settings.FONT_PATH)  # pyright: ignore[reportUnknownMemberType]
            except Exception:
                logger.error("visuals %s: failed to set custom font", self.__class__.__name__)

    @abstractmethod
    def _make_transparent_data_image(self) -> list[tuple[Path | None, Path]]: ...

    def _overlay_background(self, visuals_paths: list[tuple[Path | None, Path]]) -> list[Path]:
        image_paths: list[Path] = []

        for paths in visuals_paths:
            path_img_transparent, path_img_composed = paths

            if path_img_transparent:
                if self._img_path_background:
                    background = Image.open(self._img_path_background).convert("RGBA")
                else:
                    background = Image.new("RGBA", (1600, 800), (0, 0, 0, 255))

                bg_w, bg_h = background.size

                file_img_transparent = Image.open(path_img_transparent).convert("RGBA")
                file_img_transparent = file_img_transparent.resize((bg_w, bg_h))

                file_img_composed = Image.alpha_composite(background, file_img_transparent)
                file_img_composed = file_img_composed.convert("RGB")

                file_img_composed.save(path_img_composed)
                path_img_transparent.unlink(missing_ok=True)

                logger.debug("visuals %s: created %s", self.__class__.__name__, path_img_composed)

            image_paths.append(path_img_composed)

        return image_paths

    def create_visuals(self) -> list[Path]:
        visuals_paths = self._make_transparent_data_image()
        image_paths = self._overlay_background(visuals_paths)
        return image_paths


class Plot(Visuals):
    _plot_style = {
        "font.family": "Montserrat",
        "text.color": "#e9ecef",
        "figure.facecolor": "#e9ecef",
        "axes.facecolor": "#e9ecef",
        "axes.labelcolor": "#e9ecef",
        "axes.titlecolor": "#e9ecef",
        "axes.edgecolor": "#bbbbbb",
        "axes.labelsize": 10,
        "axes.titlesize": 20,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "xtick.color": "#e9ecef",
        "ytick.color": "#e9ecef",
        "axes.grid": True,
        "grid.color": "#f8f9fa",
        "grid.linestyle": "-",
        "grid.linewidth": 1,
        "grid.alpha": 0.6,
    }

    def __init__(self, visuals_title: str, query: Any, dataset: Any) -> None:
        super().__init__(visuals_title=visuals_title, query=query, dataset=dataset)


class Chart(Visuals):
    _plot_style = {
        "font.family": "Montserrat",
        "text.color": "#e9ecef",
        "figure.facecolor": "#e9ecef",
        "axes.facecolor": "#e9ecef",
        "axes.labelcolor": "#e9ecef",
        "axes.titlecolor": "#e9ecef",
        "axes.edgecolor": "#bbbbbb",
        "axes.labelsize": 10,
        "axes.titlesize": 20,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "xtick.color": "#e9ecef",
        "ytick.color": "#e9ecef",
        "axes.grid": True,
        "grid.color": "#f8f9fa",
        "grid.linestyle": "-",
        "grid.linewidth": 1,
        "grid.alpha": 0.6,
    }

    def __init__(self, visuals_title: str, query: Any, dataset: Any) -> None:
        super().__init__(visuals_title=visuals_title, query=query, dataset=dataset)
