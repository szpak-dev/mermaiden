import base64
import os
from typing import Literal

import pytest
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

from mermaiden import Application, ApplicationClosed, MermaidRenderFailure, PngExportOptionsError


class PngMeasurement(BaseModel):
    width: int
    height: int
    corner: tuple[int, int, int, int]
    painted_pixels: int


class TestPngRendering:
    @pytest.mark.parametrize("scale", (0, -1, float("nan"), float("inf"), float("-inf"), True))
    def test_invalid_scale_is_rejected_without_changing_state(self, scale: float) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(PngExportOptionsError, match="scale"):
                application.render_png(diagram, scale=scale)
            assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("background", ("red", ""))
    def test_invalid_background_is_rejected_without_changing_state(
        self, background: Literal["white", "transparent"]
    ) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(PngExportOptionsError, match="background"):
                application.render_png(diagram, background=background)
            assert application.snapshot(diagram).to_dict() == before

    def test_closed_handle_rejects_png_export(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.close()
        with pytest.raises(ApplicationClosed, match="closed"):
            application.render_png(diagram)

    @pytest.mark.integration
    def test_oversized_input_fails_then_same_handle_exports_literal_error_text(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Example " + "x" * 60000})
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(MermaidRenderFailure) as failure:
                application.render_png(diagram)
            assert failure.value.code == "render_failed"
            assert "MermaidTextLimitError" in failure.value.message
            assert "Maximum text size in diagram exceeded" in failure.value.details
            assert application.snapshot(diagram).to_dict() == before
            application.execute(
                diagram,
                "update_element",
                {
                    "id": "class_example",
                    "kind": "class",
                    "changes": {"label": "Example: Syntax error in text; Maximum text size in diagram exceeded"},
                },
            )
            recovered = application.snapshot(diagram).to_dict()
            image = self.measure(application.render_png(diagram))
            assert image.painted_pixels > 100
            assert application.snapshot(diagram).to_dict() == recovered

    @pytest.mark.integration
    def test_png_defaults_scaling_and_transparency_preserve_diagram_state(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(
                diagram,
                "add_class",
                {"id": "class_example", "label": 'Example & < > " ; literal &amp; &#34; #59;'},
            )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            single = self.measure(application.render_png(diagram, scale=1))
            default = self.measure(application.render_png(diagram))
            transparent = self.measure(application.render_png(diagram, background="transparent"))
            assert abs(default.width - single.width * 2) <= 1
            assert abs(default.height - single.height * 2) <= 1
            assert (transparent.width, transparent.height) == (default.width, default.height)
            assert single.corner == default.corner == (255, 255, 255, 255)
            assert transparent.corner[3] == 0
            assert min(single.painted_pixels, default.painted_pixels, transparent.painted_pixels) > 100
            assert application.snapshot(diagram).to_dict() == before
            assert application.render(diagram) == source

    def measure(self, content: bytes) -> PngMeasurement:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get("SVG_VIEWER_EXECUTABLE_PATH"))
            try:
                page = browser.new_page()
                return PngMeasurement.model_validate(
                    page.evaluate(
                        """async (encoded) => {
                            const image = new Image();
                            image.src = `data:image/png;base64,${encoded}`;
                            await image.decode();
                            const canvas = document.createElement('canvas');
                            canvas.width = image.naturalWidth;
                            canvas.height = image.naturalHeight;
                            const context = canvas.getContext('2d');
                            context.drawImage(image, 0, 0);
                            const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
                            let painted = 0;
                            for (let index = 0; index < pixels.length; index += 4) {
                                if (pixels[index + 3] > 0 &&
                                    (pixels[index] < 245 || pixels[index + 1] < 245 || pixels[index + 2] < 245)) {
                                    painted++;
                                }
                            }
                            return {
                                width: canvas.width,
                                height: canvas.height,
                                corner: Array.from(pixels.slice(0, 4)),
                                painted_pixels: painted,
                            };
                        }""",
                        base64.b64encode(content).decode("ascii"),
                    )
                )
            finally:
                browser.close()
