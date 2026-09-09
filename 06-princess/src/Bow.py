"""
This file contains the bow and its arrow factory.
"""

from typing import Any

import pygame

import settings
from src.GameObject import GameObject
from src.Projectile import Projectile
from src.definitions.game_objects import GAME_OBJECT_DEFS


class ArrowFactory:
    """Creates the GameObject consumed by Projectile for each arrow."""

    _ARROW_FRAME = 3
    _ROTATIONS = {"right": 0, "up": 90, "left": 180, "down": 270}

    @classmethod
    def create(cls, player: Any) -> Projectile:
        direction = player.direction
        arrow = GameObject(
            GAME_OBJECT_DEFS["arrow"],
            player.x,
            player.y + player.height / 2 - 8,
        )
        arrow.frame_index = cls._ARROW_FRAME
        arrow.rotation = cls._ROTATIONS[direction]

        if direction == "up":
            arrow.x = player.x
            arrow.y = player.y - arrow.height
        elif direction == "down":
            arrow.x = player.x
            arrow.y = player.y + player.height
        elif direction == "left":
            arrow.x = player.x - arrow.width
            arrow.y = player.y + player.height / 2 - arrow.height / 2
        else:
            arrow.x = player.x + player.width
            arrow.y = player.y + player.height / 2 - arrow.height / 2

        return Projectile(arrow, direction)


class Bow:
    _ANIMATION_FRAMES = (1, 2, 4, 5)
    _ANIMATION_INTERVAL = 0.12
    _OFFSETS = {
        "up": (-2, -1),
        "down": (2, 7),
        "left": (-5, 7),
        "right": (5, 7),
    }

    def __init__(self, player: Any) -> None:
        self.player = player
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_active = False

    def update(self, dt: float) -> None:
        if not self.animation_active:
            return

        self.animation_timer += dt
        while self.animation_timer >= self._ANIMATION_INTERVAL:
            self.animation_timer -= self._ANIMATION_INTERVAL
            self.animation_index += 1
            if self.animation_index >= len(self._ANIMATION_FRAMES):
                self.animation_index = 0
                self.animation_active = False
                break

    def render(self, surface: pygame.Surface) -> None:
        frame = settings.frame(
            "bow_arrows", self._ANIMATION_FRAMES[self.animation_index]
        )
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(settings.TEXTURES["bow_arrows"], (0, 0), frame)

        player = self.player
        if player.direction == "left":
            image = pygame.transform.flip(image, True, False)

        offset_x, offset_y = self._OFFSETS[player.direction]
        surface.blit(
            image,
            (
                round(player.x - player.offset_x + offset_x),
                round(player.y - player.offset_y + offset_y),
            ),
        )

    def fire(self, projectiles: list) -> None:
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_active = True
        projectiles.append(ArrowFactory.create(self.player))