"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False
        self.dragged_tile = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_axis = None
        self.shuffling = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 2 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            if self.shuffling:
                return

            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.shuffling:
            return

        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.shuffling:
            shuffling_font = settings.FONTS["large"]
            shuffling_width, shuffling_height = shuffling_font.size(
                "shuffling"
            )
            board_center_x = self.board.x + settings.BOARD_WIDTH * settings.TILE_SIZE // 2
            board_center_y = self.board.y + settings.BOARD_HEIGHT * settings.TILE_SIZE // 2
            render_text(
                surface,
                "shuffling",
                shuffling_font,
                board_center_x - shuffling_width // 2,
                board_center_y - shuffling_height // 2,
                (255, 255, 255),
                shadowed=True,
            )

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            if input_data.pressed:
                self._start_drag(input_data.position)
            elif input_data.released:
                self._finish_drag(input_data.position)
        elif input_id == "click_motion" and self.dragged_tile is not None:
            self._update_drag(input_data.position)

    def _mouse_to_board_position(self, position) -> tuple[int, int]:
        pos_x = position[0] * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
        pos_y = position[1] * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
        return pos_x - self.board.x, pos_y - self.board.y

    def _board_cell_at(self, position) -> tuple[int, int] | None:
        board_x, board_y = self._mouse_to_board_position(position)
        i = board_y // settings.TILE_SIZE
        j = board_x // settings.TILE_SIZE

        if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
            return i, j
        return None

    def _start_drag(self, position) -> None:
        cell = self._board_cell_at(position)
        if cell is None:
            return

        i, j = cell
        self.dragged_tile = self.board.tiles[i][j]
        self.drag_start_x = j * settings.TILE_SIZE
        self.drag_start_y = i * settings.TILE_SIZE
        self.dragged_tile.x = self.drag_start_x
        self.dragged_tile.y = self.drag_start_y
        board_x, board_y = self._mouse_to_board_position(position)
        self.drag_offset_x = board_x - self.dragged_tile.x
        self.drag_offset_y = board_y - self.dragged_tile.y
        self.drag_axis = None
        self.highlighted_tile = True
        self.highlighted_i1 = i
        self.highlighted_j1 = j
        settings.SOUNDS["select"].play()

    def _update_drag(self, position) -> None:
        board_x, board_y = self._mouse_to_board_position(position)
        delta_x = board_x - self.drag_offset_x - self.drag_start_x
        delta_y = board_y - self.drag_offset_y - self.drag_start_y

        if self.drag_axis is None and (delta_x != 0 or delta_y != 0):
            self.drag_axis = "horizontal" if abs(delta_x) >= abs(delta_y) else "vertical"

        max_drag = settings.TILE_SIZE
        if self.drag_axis == "horizontal":
            delta_x = max(-max_drag, min(max_drag, delta_x))
            self.dragged_tile.x = self.drag_start_x + delta_x
            self.dragged_tile.y = self.drag_start_y
        elif self.drag_axis == "vertical":
            delta_y = max(-max_drag, min(max_drag, delta_y))
            self.dragged_tile.x = self.drag_start_x
            self.dragged_tile.y = self.drag_start_y + delta_y
        else:
            self.dragged_tile.x = self.drag_start_x
            self.dragged_tile.y = self.drag_start_y

    def _finish_drag(self, position) -> None:
        tile1 = self.dragged_tile
        if tile1 is None:
            return

        self._update_drag(position)
        origin_i, origin_j = self.highlighted_i1, self.highlighted_j1
        delta_x = self.dragged_tile.x - self.drag_start_x
        delta_y = self.dragged_tile.y - self.drag_start_y
        self.dragged_tile = None
        self.highlighted_tile = False

        if self.drag_axis is None or max(abs(delta_x), abs(delta_y)) < settings.TILE_SIZE // 2:
            if tile1.power_up is not None:
                self.active = False
                self.board.activate_power_up(origin_i, origin_j)
                self._process_matches()
                return
            self._return_tile(tile1, origin_i, origin_j)
            return

        target_i, target_j = origin_i, origin_j
        if self.drag_axis == "horizontal":
            target_j += 1 if delta_x > 0 else -1
        else:
            target_i += 1 if delta_y > 0 else -1

        if not (
            0 <= target_i < settings.BOARD_HEIGHT
            and 0 <= target_j < settings.BOARD_WIDTH
        ):
            self._return_tile(tile1, origin_i, origin_j)
            return

        if not self.board.is_valid_move(origin_i, origin_j, target_i, target_j):
            self._return_tile(tile1, origin_i, origin_j)
            return

        tile2 = self.board.tiles[target_i][target_j]
        tile1_start_x, tile1_start_y = self.drag_start_x, self.drag_start_y
        tile2_start_x = target_j * settings.TILE_SIZE
        tile2_start_y = target_i * settings.TILE_SIZE
        self.active = False

        def arrive():
            (
                self.board.tiles[origin_i][origin_j],
                self.board.tiles[target_i][target_j],
            ) = (
                tile2,
                tile1,
            )
            tile1.i, tile1.j = target_i, target_j
            tile2.i, tile2.j = origin_i, origin_j
            self._calculate_matches([tile1, tile2], (target_i, target_j))

        Timer.tween(
            0.25,
            [
                (tile1, {"x": tile2_start_x, "y": tile2_start_y}),
                (tile2, {"x": tile1_start_x, "y": tile1_start_y}),
            ],
            on_finish=arrive,
        )

    def _return_tile(self, tile, i: int, j: int) -> None:
        Timer.tween(
            0.15,
            [
                (
                    tile,
                    {"x": j * settings.TILE_SIZE, "y": i * settings.TILE_SIZE},
                )
            ],
        )

    def _calculate_matches(
        self, tiles: List, power_up_position: tuple[int, int] | None = None
    ) -> None:
        matches = self.board.calculate_matches_for(tiles, power_up_position)

        if matches is None:
            if self.board.ensure_possible_move():
                self._animate_shuffle()
            else:
                self.active = True
            return

        self._process_matches()

    def _process_matches(self) -> None:
        matches = self.board.matches

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )

    def _animate_shuffle(self) -> None:
        self.shuffling = True
        self.active = False
        tweens = []

        for row in self.board.tiles:
            for tile in row:
                target_y = tile.y
                tile.y -= settings.TILE_SIZE
                tweens.append((tile, {"y": target_y}))

        Timer.tween(1.0, tweens, on_finish=self._finish_shuffle)

    def _finish_shuffle(self) -> None:
        self.shuffling = False
        self.active = True
