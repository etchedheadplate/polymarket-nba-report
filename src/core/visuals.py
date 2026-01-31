import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from matplotlib import font_manager as fm
from PIL import Image

from src.config import settings
from src.logger import logger


class Visuals(ABC):
    _ext = "png"
    _shared_dir = settings.SHARED_DIR
    _data_font_path = settings.VISUALS_FONT_PATH
    _output_dir: str
    _image_bg_path: Path

    def __init__(self, input_data: Any) -> None:
        self._input_data = input_data
        os.makedirs(self._shared_dir, exist_ok=True)

        try:
            fm.fontManager.addfont(self._data_font_path)  # type: ignore[attr-defined]
        except Exception:
            logger.error("Failed to set custom font")

    @abstractmethod
    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]: ...

    def _overlay_background(self, visuals_paths: list[tuple[Path, Path]]) -> list[Path]:
        image_paths: list[Path] = []

        for paths in visuals_paths:
            path_without_bg, path_with_bg = paths

            background = Image.open(self._image_bg_path).convert("RGBA")
            image_without_bg = Image.open(path_without_bg).convert("RGBA")

            bg_w, bg_h = background.size
            image_without_bg = image_without_bg.resize((bg_w, bg_h))

            image_with_bg = Image.alpha_composite(background, image_without_bg)
            image_with_bg.save(path_with_bg)
            logger.debug("Created: %s", path_with_bg)

            image_paths.append(path_with_bg)
            path_without_bg.unlink(missing_ok=True)

        return image_paths

    def create_visuals(self) -> list[Path]:
        visuals_paths = self._make_transparent_data_image()
        image_paths = self._overlay_background(visuals_paths)
        return image_paths


class Plot(Visuals):
    _output_dir = "plots"
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

    def __init__(self, input_data: Any) -> None:
        super().__init__(input_data)
        self._plot_dir = self._shared_dir / self._output_dir
        os.makedirs(self._plot_dir, exist_ok=True)


class Chart(Visuals):
    _output_dir = "charts"
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

    def __init__(self, input_data: Any) -> None:
        super().__init__(input_data)
        self._chart_dir = self._shared_dir / self._output_dir
        os.makedirs(self._chart_dir, exist_ok=True)
