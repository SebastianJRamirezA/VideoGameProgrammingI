"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Projectile.
"""

import math
from typing import Any, Tuple

import pygame

import settings

_SPEED = 150
_MAX_TILES = 4


class Projectile:
    def __init__(
        self,
        obj: Any,
        direction: Any,
        speed: float = _SPEED,
        owner: Any = None,
        kind: str = "object",
    ) -> None:
        self.obj = obj
        self.direction = direction
        self.speed = speed
        self.owner = owner
        self.kind = kind
        self.distance = 0.0
        self.dead = False

        if isinstance(direction, str):
            directions = {
                "up": (0.0, -1.0),
                "down": (0.0, 1.0),
                "left": (-1.0, 0.0),
                "right": (1.0, 0.0),
            }
            self.velocity: Tuple[float, float] = directions[direction]
        else:
            length = math.hypot(direction[0], direction[1]) or 1.0
            self.velocity = (direction[0] / length, direction[1] / length)

    def get_collision_rect(self) -> pygame.Rect:
        return self.obj.get_collision_rect()

    def update(self, dt: float) -> None:
        if self.dead:
            return

        distance = self.speed * dt
        self.obj.x += self.velocity[0] * distance
        self.obj.y += self.velocity[1] * distance

        left = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        top = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        right = settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2
        bottom = settings.MAP_HEIGHT * settings.TILE_SIZE + settings.MAP_RENDER_OFFSET_Y - settings.TILE_SIZE
        if (
            self.obj.x < left
            or self.obj.x + self.obj.width > right
            or self.obj.y < top
            or self.obj.y + self.obj.height > bottom
        ):
            self.dead = True

        if self.dead:
            settings.SOUNDS["pot-wall"].play()
            return

        self.distance += distance

        if self.distance > _MAX_TILES * settings.TILE_SIZE:
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        self.obj.render(surface, offset_x, offset_y)

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
