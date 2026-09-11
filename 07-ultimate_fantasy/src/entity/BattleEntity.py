"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class BattleEntity: adds battle stats (HP/attack/
defense/magic) and the damage/heal/compute-* formulas shared by both
Character (playable) and Enemy.
"""

import math
import random
from typing import Any, Dict, List

from src.entity.Entity import Entity


DEFAULT_REST_TIMES = {
    "warrior": 2.8,
    "ranger": 1.4,
    "healer": 1.9,
    "mage": 2.2,
    "slime": 2.0,
    "worm": 2.4,
    "snake": 1.7,
    "pumpking": 2.8,
    "boss": 3.6,
}


class BattleEntity(Entity):
    def __init__(self, definition: Dict[str, Any]) -> None:
        super().__init__(definition)

        self.klass: str = definition["class"]
        self.actions: List[Dict[str, Any]] = definition["actions"]
        self.level: int = definition.get("level", 1)
        self.dead: bool = definition.get("dead", False)

        self.base_hp: float = definition["baseHP"]
        self.base_attack: float = definition["baseAttack"]
        self.base_defense: float = definition["baseDefense"]
        self.base_magic: float = definition["baseMagic"]

        self.hp: float = self.base_hp
        self.attack: float = self.base_attack
        self.defense: float = self.base_defense
        self.magic: float = self.base_magic

        self.current_hp: float = self.hp
        self.rest_time: float = definition.get(
            "rest_time", DEFAULT_REST_TIMES.get(self.klass, 2.0)
        )
        self.initial_rest_time: float = definition.get(
            "initial_rest_time", self.rest_time * 0.35
        )
        self.rest_timer: float = self.initial_rest_time
        self.pending_action: Dict[str, Any] = {}

    def update_rest(self, dt: float) -> None:
        self.rest_timer = max(0.0, self.rest_timer - dt)

    def start_rest(self, action: Dict[str, Any] = None) -> None:
        self.rest_timer = (action or {}).get("rest_time", self.rest_time)

    def reset_rest_for_battle(self) -> None:
        self.rest_timer = self.initial_rest_time
        self.pending_action = {}

    def max_rest_time(self) -> float:
        return max(
            self.rest_time,
            *(action.get("rest_time", self.rest_time) for action in self.actions),
        )

    def ready_to_act(self) -> bool:
        return not self.dead and self.rest_timer <= 0

    def damage(self, amount: float) -> None:
        self.current_hp -= amount

        if self.current_hp <= 0:
            self.dead = True

    def heal(self, amount: float) -> None:
        if not self.dead:
            self.current_hp = min(self.hp, self.current_hp + amount)

    def compute_attack(self) -> int:
        return math.floor(random.random() / 2 * self.attack + random.random() / 4 * self.magic)

    def compute_defense(self) -> int:
        return math.floor(
            random.random() / 4 * self.defense + random.random() / 8 * self.magic
        )

    def compute_healing(self) -> int:
        return math.floor(random.random() * 2 * self.magic)
