"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.preserved_tiles: Set[Tile] = set()
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()
        self.ensure_possible_move()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def _creates_match(self, colors: List[List[int]], i: int, j: int) -> bool:
        color = colors[i][j]

        horizontal = 1
        column = j - 1
        while column >= 0 and colors[i][column] == color:
            horizontal += 1
            column -= 1
        column = j + 1
        while column < settings.BOARD_WIDTH and colors[i][column] == color:
            horizontal += 1
            column += 1

        if horizontal >= 3:
            return True

        vertical = 1
        row = i - 1
        while row >= 0 and colors[row][j] == color:
            vertical += 1
            row -= 1
        row = i + 1
        while row < settings.BOARD_HEIGHT and colors[row][j] == color:
            vertical += 1
            row += 1

        return vertical >= 3

    def has_possible_moves(self) -> bool:
        colors = [[tile.color for tile in row] for row in self.tiles]

        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                for next_i, next_j in ((i + 1, j), (i, j + 1)):
                    if next_i >= settings.BOARD_HEIGHT or next_j >= settings.BOARD_WIDTH:
                        continue

                    if self._is_valid_move(colors, i, j, next_i, next_j):
                        return True

        return False

    def is_valid_move(self, i: int, j: int, next_i: int, next_j: int) -> bool:
        colors = [[tile.color for tile in row] for row in self.tiles]
        return self._is_valid_move(colors, i, j, next_i, next_j)

    def _is_valid_move(
        self,
        colors: List[List[int]],
        i: int,
        j: int,
        next_i: int,
        next_j: int,
    ) -> bool:
        colors[i][j], colors[next_i][next_j] = (
            colors[next_i][next_j],
            colors[i][j],
        )
        creates_match = self._creates_match(colors, i, j) or self._creates_match(
            colors, next_i, next_j
        )
        colors[i][j], colors[next_i][next_j] = (
            colors[next_i][next_j],
            colors[i][j],
        )
        return creates_match

    def ensure_possible_move(self) -> bool:
        reshuffled = False
        while not self.has_possible_moves():
            self._initialize_tiles()
            reshuffled = True
        return reshuffled

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile], power_up_position: Optional[Tuple[int, int]] = None
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        preserved_tiles: Set[Tile] = set()
        if power_up_position is not None:
            power_up_i, power_up_j = power_up_position
            power_up_tile = self.tiles[power_up_i][power_up_j]
            for match in self.matches:
                if len(match) == 4 and power_up_tile in match:
                    power_up_tile.power_up = "line"
                    preserved_tiles.add(power_up_tile)
                    break
                if len(match) >= 5 and power_up_tile in match:
                    power_up_tile.power_up = "color_bomb"
                    preserved_tiles.add(power_up_tile)
                    break

        self._expand_power_up_matches(preserved_tiles)
        self.preserved_tiles = preserved_tiles

        return self.matches if len(self.matches) > 0 else None

    def _expand_power_up_matches(self, preserved_tiles: Set[Tile]) -> None:
        expanded_matches = []
        for match in self.matches:
            expanded_match = list(match)
            for tile in match:
                if tile in preserved_tiles or tile.power_up is None:
                    continue

                if tile.power_up == "line":
                    for row_tile in self.tiles[tile.i]:
                        if row_tile not in expanded_match:
                            expanded_match.append(row_tile)
                    for row in self.tiles:
                        column_tile = row[tile.j]
                        if column_tile not in expanded_match:
                            expanded_match.append(column_tile)
                elif tile.power_up == "color_bomb":
                    for row in self.tiles:
                        for color_tile in row:
                            if (
                                color_tile is not None
                                and color_tile.color == tile.color
                                and color_tile not in expanded_match
                            ):
                                expanded_match.append(color_tile)
            expanded_matches.append(expanded_match)
        self.matches = expanded_matches

    def activate_power_up(self, i: int, j: int) -> None:
        tile = self.tiles[i][j]
        if not tile.power_up:
            return

        if tile.power_up == "color_bomb":
            affected_tiles = [
                board_tile
                for row in self.tiles
                for board_tile in row
                if board_tile is not None and board_tile.color == tile.color
            ]
        else:
            affected_tiles = list(self.tiles[i])
            for row in self.tiles:
                if row[j] not in affected_tiles:
                    affected_tiles.append(row[j])
        self.matches = [affected_tiles]
        self.preserved_tiles = set()

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                if tile in self.preserved_tiles:
                    continue
                self.tiles[tile.i][tile.j] = None

        self.matches = []
        self.preserved_tiles = set()

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens
