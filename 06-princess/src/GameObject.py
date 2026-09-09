"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameObject.
"""

from typing import Any, Dict

import pygame
from gale.animation import Animation

import settings


class GameObject:
    def __init__(self, definition: Dict[str, Any], x: float, y: float) -> None:
        self.type = definition["type"]
        self.texture_id = definition["texture"]
        self.frame_index = definition.get("frame", 1)

        # Whether it acts as an obstacle or not.
        self.solid = definition["solid"]

        self.default_state = definition["default_state"]
        self.state = self.default_state
        self.states = definition["states"]
        self.animation_frames = definition.get("animation_frames", {})
        self.animations = {
            state: Animation(
                animation["frames"],
                animation["interval"],
                loops=1,
                on_finish=lambda state=state, animation=animation: self._finish_animation(
                    state, animation
                ),
            )
            for state, animation in self.animation_frames.items()
        }
        self._animation_state = None

        self.x = x
        self.y = y
        self.width = definition["width"]
        self.height = definition["height"]

        self.on_collide = definition.get("on_collide") or (lambda: None)

        # Whether this object is consumable or not.
        self.consumable = definition.get("consumable", False)
        self.on_consume = definition.get("on_consume") or (lambda player, obj: None)

        # An object could be taken or not.
        self.takeable = definition.get("takeable", False)
        self.taken = False

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        animation = self.animations.get(self.state)
        if animation is None:
            return

        if self._animation_state != self.state:
            animation.reset()
            self._animation_state = self.state

        animation.update(dt)

    def _finish_animation(self, state: str, definition: Dict[str, Any]) -> None:
        if self.state == state:
            self.state = definition.get("finished_state", state)

    def _frame_index(self) -> int:
        animation = self.animations.get(self.state)
        if animation is not None:
            return animation.get_current_frame()
        return self.states[self.state].get("frame", self.frame_index)

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        frame = settings.frame(self.texture_id, self._frame_index())
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(settings.TEXTURES[self.texture_id], (0, 0), frame)

        if getattr(self, "rotation", 0):
            image = pygame.transform.rotate(image, self.rotation)

        surface.blit(image, (self.x + offset_x, self.y + offset_y))
