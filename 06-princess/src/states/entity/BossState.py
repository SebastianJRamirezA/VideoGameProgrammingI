"""AI state for the boss in the boss room."""

import math
from typing import Any

from src.GameObject import GameObject
from src.Projectile import Projectile
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.states.entity.BaseEntityState import BaseEntityState


class BossState(BaseEntityState):
    _FIRE_INTERVAL = 2.0
    _FIREBALL_SPEED = 45.0

    def enter(self) -> None:
        self.entity.change_animation("idle-down")
        self.fire_timer = self._FIRE_INTERVAL

    def process_ai(self, room: Any, dt: float) -> None:
        if self.entity.vulnerable_timer > 0:
            self.fire_timer = 0.0
            return

        self.fire_timer += dt
        if self.fire_timer < self._FIRE_INTERVAL:
            return

        self.fire_timer = 0.0
        boss_center = (
            self.entity.x + self.entity.width / 2,
            self.entity.y + self.entity.height / 2,
        )
        player_center = (
            room.player.x + room.player.width / 2,
            room.player.y + room.player.height / 2,
        )
        dx = player_center[0] - boss_center[0]
        dy = player_center[1] - boss_center[1]
        distance = math.hypot(dx, dy) or 1.0
        velocity = (dx / distance, dy / distance)

        fireball = GameObject(
            GAME_OBJECT_DEFS["fireball"],
            boss_center[0] - 8,
            boss_center[1] - 8,
        )
        fireball.rotation = math.degrees(math.atan2(-velocity[1], velocity[0]))
        room.projectiles.append(
            Projectile(
                fireball,
                velocity,
                speed=self._FIREBALL_SPEED,
                owner=self.entity,
                kind="fireball",
            )
        )

    def render(self, surface) -> None:
        animation = self.entity.current_animation
        self.entity.render_sprite(surface, animation.texture_id, animation.get_current_frame())