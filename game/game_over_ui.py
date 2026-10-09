"""Game Over UI and Life Summary Screen.

Displays 'FLY CAUGHT' or 'STARVED TO DEATH' and a clean, responsive Life Summary
report that fits comfortably on screen without horizontal text clipping.
"""
from __future__ import annotations

from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, Vec4


class GameOverUI:
    def __init__(self, on_retry_callback):
        self.on_retry = on_retry_callback
        self.is_visible = False

        # Semi-transparent dark overlay frame
        self.frame = DirectFrame(
            frameColor=(0.04, 0.04, 0.07, 0.90),
            frameSize=(-1.4, 1.4, -1.0, 1.0),
            pos=(0, 0, 0)
        )
        self.frame.hide()

        # Dynamic Death Title (FLY CAUGHT / STARVED TO DEATH)
        self.title = OnscreenText(
            text="FLY CAUGHT!",
            parent=self.frame,
            pos=(0, 0.52),
            scale=0.10,
            fg=Vec4(0.95, 0.20, 0.20, 1.0),
            align=TextNode.ACenter,
            mayChange=True
        )

        # Dynamic Subtitle
        self.subtitle = OnscreenText(
            text="A frog predator snatched you with its tongue!",
            parent=self.frame,
            pos=(0, 0.40),
            scale=0.044,
            fg=Vec4(0.85, 0.85, 0.90, 1.0),
            align=TextNode.ACenter,
            mayChange=True
        )

        # Life Summary Text Box (Responsive, clean typography)
        self.summary_text = OnscreenText(
            text="",
            parent=self.frame,
            pos=(0, 0.25),
            scale=0.038,
            fg=Vec4(1.0, 0.92, 0.35, 1.0),
            align=TextNode.ACenter,
            mayChange=True
        )

        # Clickable RETRY Button
        self.retry_btn = DirectButton(
            text="RETRY [R]",
            parent=self.frame,
            scale=0.060,
            pos=(0, 0, -0.42),
            frameColor=(0.18, 0.65, 0.24, 1.0),
            text_fg=(1, 1, 1, 1),
            pad=(0.35, 0.18),
            command=self._handle_retry
        )

    def show(self, cause: str, alive_time: float, food_eaten: int, distance: float,
             landings: int, encounters: int, escapes: int, associations: int = 0):
        self.is_visible = True

        if cause == "FROG":
            self.title.setText("FLY CAUGHT!")
            self.title.setFg(Vec4(0.95, 0.20, 0.20, 1.0))
            self.subtitle.setText("A frog predator snatched you with its tongue!")
        else:
            self.title.setText("STARVED TO DEATH!")
            self.title.setFg(Vec4(0.98, 0.65, 0.15, 1.0))
            self.subtitle.setText("Energy reached 0.0 before finding food.")

        summary_lines = [
            "--- LIFE SUMMARY ---",
            f"LIFETIME: {alive_time:.1f}s",
            f"FOOD EATEN: {food_eaten}",
            f"DISTANCE: {distance:.1f}m",
            f"TOTAL LANDINGS: {landings}",
            f"FROG ENCOUNTERS: {encounters}",
            f"NEURAL ESCAPES: {escapes}",
            f"MEMORIES PERSISTED: {associations} pairs",
        ]
        self.summary_text.setText("\n".join(summary_lines))
        self.frame.show()

    def hide(self):
        self.is_visible = False
        self.frame.hide()

    def _handle_retry(self):
        self.hide()
        if self.on_retry:
            self.on_retry()
