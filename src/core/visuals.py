import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from matplotlib import font_manager as fm
from PIL import Image

from src.config import settings
from src.logger import logger


class Visuals(ABC):
    _visuals_title: str
    _img_output_dir: str
    _img_ext_transp: str = "png"
    _img_ext_final: str = "jpg"
    _path_shared_dir: Path = settings.SHARED_DIR
    _path_img_font: Path = settings.VISUALS_FONT_PATH
    _path_img_bg: Path
    _img_params: dict[str, Any]

    def __init__(self, query: Any, dataset: Any) -> None:
        self._query = query
        self._dataset = dataset
        os.makedirs(self._path_shared_dir / self._img_output_dir, exist_ok=True)

        try:
            fm.fontManager.addfont(self._path_img_font)  # pyright: ignore[reportUnknownMemberType]
        except Exception:
            logger.error("visuals %s: failed to set custom font", self.__class__.__name__)

    @abstractmethod
    def _make_transparent_data_image(self) -> list[tuple[Path | None, Path]]: ...

    def _overlay_background(self, visuals_paths: list[tuple[Path | None, Path]]) -> list[Path]:
        image_paths: list[Path] = []

        for paths in visuals_paths:
            path_without_bg, path_with_bg = paths

            if path_without_bg:
                background = Image.open(self._path_img_bg).convert("RGBA")
                image_without_bg = Image.open(path_without_bg).convert("RGBA")

                bg_w, bg_h = background.size
                image_without_bg = image_without_bg.resize((bg_w, bg_h))

                image_with_bg = Image.alpha_composite(background, image_without_bg)
                image_with_bg = image_with_bg.convert("RGB")
                image_with_bg.save(path_with_bg)
                path_without_bg.unlink(missing_ok=True)

                logger.debug("visuals %s: created %s", self.__class__.__name__, path_with_bg)

            image_paths.append(path_with_bg)

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

    def __init__(self, query: Any, dataset: Any) -> None:
        super().__init__(query=query, dataset=dataset)
        self._plot_dir = self._path_shared_dir / self._img_output_dir
        os.makedirs(self._plot_dir, exist_ok=True)


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

    def __init__(self, query: Any, dataset: Any) -> None:
        super().__init__(query=query, dataset=dataset)
        self._chart_dir = self._path_shared_dir / self._img_output_dir
        os.makedirs(self._chart_dir, exist_ok=True)
