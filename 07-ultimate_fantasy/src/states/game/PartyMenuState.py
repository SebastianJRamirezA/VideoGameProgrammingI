"""Party status and out-of-battle healing menu."""

from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.gui.Panel import Panel


class PartyMenuState(BaseState):
    """Shows party status and permits the character healing actions."""

    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        self.party = play_state.world.party
        self.characters = list(self.party.characters.values())
        self.character_index = 0
        self.action_index = 0

    def _selected_character(self) -> Any:
        return self.characters[self.character_index]

    def _selected_action(self) -> Any:
        actions = self._selected_character().actions
        return actions[self.action_index] if actions else None

    def _is_healing(self, action: Any) -> bool:
        return action.get("target_type") == "character"

    def _move_character(self, direction: int) -> None:
        self.character_index = (self.character_index + direction) % len(self.characters)
        self.action_index = 0

    def _move_action(self, direction: int) -> None:
        actions = self._selected_character().actions
        if actions:
            self.action_index = (self.action_index + direction) % len(actions)

    def _select_action(self) -> None:
        action = self._selected_action()
        if action is None or not self._is_healing(action):
            return

        from src.states.game.SelectTargetState import SelectTargetState

        targets = [character for character in self.characters if not character.dead]
        if not targets:
            return

        if action["require_target"]:
            self.state_machine.push(
                SelectTargetState(self.state_machine),
                battle_state=self.play_state,
                targets=targets,
                on_target_selected=lambda target: self._resolve(action, target),
            )
        else:
            action["func"](self._selected_character(), targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            self.play_state.world.dirty = True

    def _resolve(self, action: Any, target: Any) -> None:
        action["func"](self._selected_character(), target, action.get("strength"))
        settings.SOUNDS[action["sound_effect"]].play()
        self.play_state.world.dirty = True

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_left":
            self._move_character(-1)
        elif input_id == "move_right":
            self._move_character(1)
        elif input_id == "move_up":
            self._move_action(-1)
        elif input_id == "move_down":
            self._move_action(1)
        elif input_id == "enter":
            self._select_action()
        elif input_id == "pause" or input_id == "quit":
            self.state_machine.pop()

    def update(self, dt: float) -> None:
        pass

    def _text(self, surface: pygame.Surface, text: str, position: Any, alpha: int = 255) -> None:
        image = settings.FONTS["small"].render(text, False, (255, 255, 255))
        image.set_alpha(alpha)
        surface.blit(image, position)

    def _draw_card(self, surface: pygame.Surface, character: Any, rect: pygame.Rect, selected: bool) -> None:
        Panel(rect.x, rect.y, rect.width, rect.height).render(surface)
        if selected:
            pygame.draw.rect(surface, (255, 220, 80), rect, width=1)

        self._text(surface, character.name, (rect.x + 5, rect.y + 4))
        self._text(surface, f"LV {character.level}  MAG {character.magic}", (rect.x + 5, rect.y + 16))
        self._text(surface, f"HP {int(character.current_hp)}/{int(character.hp)}", (rect.x + 5, rect.y + 28))
        self._text(
            surface,
            f"EXP {int(character.current_exp)}/{int(character.exp_to_level)}",
            (rect.x + 5, rect.y + 40),
        )

        for index, action in enumerate(character.actions):
            alpha = 255 if self._is_healing(action) else 110
            if selected and index == self.action_index:
                pygame.draw.rect(
                    surface,
                    (80, 80, 80),
                    pygame.Rect(rect.x + 3, rect.y + 53 + index * 9, rect.width - 6, 9),
                )
            self._text(surface, action["name"], (rect.x + 7, rect.y + 53 + index * 9), alpha)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        self._text(surface, "PARTY", (8, 7))

        card_width = 92
        card_height = 78
        for index, character in enumerate(self.characters):
            rect = pygame.Rect(
                8 + (index % 4) * (card_width + 3),
                22,
                card_width,
                card_height,
            )
            self._draw_card(surface, character, rect, index == self.character_index)