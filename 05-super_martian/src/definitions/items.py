"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for items.
"""

from typing import Dict, Any

import random

from gale.timer import Timer

import settings
from src.GameItem import GameItem
from src.Player import Player


def pickup_coin(
    coin: GameItem, player: Player, points: int, color: int, time: float
) -> None:
    settings.SOUNDS["pickup_coin"].stop()
    settings.SOUNDS["pickup_coin"].play()
    player.score += points
    player.coins_counter[color] += 1
    Timer.after(time, lambda: coin.respawn())


def pickup_green_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 1, 62, random.uniform(2, 4))


def pickup_blue_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 5, 61, random.uniform(5, 8))


def pickup_red_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 20, 55, random.uniform(10, 18))


def pickup_yellow_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 50, 54, random.uniform(20, 25))


def special_block_on_collide(block: GameItem, player: Player):
    if getattr(block, "triggered", False):
        return None

    block_rect = block.get_collision_rect()
    player_rect = player.get_collision_rect()

    is_from_below = (
        player.vy < 0
        and player_rect.top >= block_rect.bottom - 6
        and player_rect.top <= block_rect.bottom + 12
        and player_rect.right > block_rect.left
        and player_rect.left < block_rect.right
    )

    if is_from_below:
        block.triggered = True
        block.active = False
        block.collidable = False
        player.vy = 140
        player.y = block_rect.bottom + 1
        if block.game_level is not None:
            block.game_level.spawn_key_from_special_block(block)
    return None


def pickup_key(key: GameItem, player: Player):
    key.active = False
    player.score += 100
    if hasattr(player, "game_level"):
        player.game_level.finish_level()
    return None


ITEMS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "coins": {
        62: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_green_coin,
        },
        61: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_blue_coin,
        },
        55: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_red_coin,
        },
        54: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_yellow_coin,
        },
    },
    "special_block": {
        0: {
            "texture_id": "tiles",
            "frame_index": 41,
            "consumable": False,
            "collidable": True,
            "on_collide": special_block_on_collide,
        },
        50: {
            "texture_id": "tiles",
            "frame_index": 50,
            "consumable": False,
            "collidable": True,
            "on_collide": special_block_on_collide,
        },
    },
    "key": {
        0: {
            "texture_id": "tiles",
            "frame_index": 36,
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_key,
        },
        64: {
            "texture_id": "tiles",
            "frame_index": 64,
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_key,
        },
    },
}
