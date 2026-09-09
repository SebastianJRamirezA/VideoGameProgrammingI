# Breakout

## How to Play

Run the game from this directory:

```bash
python main.py
```

Break all the bricks with the ball while keeping the ball in play. Catching
power-ups with the paddle gives temporary abilities or additional balls. You
start with three lives; losing all of them ends the game. Clear the level to
advance and earn points to gain extra lives and grow the paddle.

## Controls

| Key | Action |
| --- | --- |
| Left Arrow | Move the paddle left |
| Right Arrow | Move the paddle right |
| Enter | Serve the ball or release a ball caught by the sticky paddle |
| F | Fire the mounted paddle cannons |
| Space | Pause or resume the game |
| Escape | Quit the game |

## Power-Ups

Power-ups fall from destroyed bricks. Move the paddle under one to collect it.

1. **Catch Ball / Sticky Paddle (🎾)**
	- The ball sticks to the paddle instead of bouncing when it hits.
	- Move the paddle to position the ball, then press **Enter** to launch it.
	- The effect lasts for a limited time.

2. **Paddle Cannons (🚀)**
	- Mounts cannons on both sides of the paddle.
	- Press **F** to fire two vertical bullets at the bricks.
	- The power-up is consumed after firing.

3. **Explosive Ball (✨)**
	- Makes the active balls explosive for a limited time.
	- Hitting a brick also destroys its neighboring bricks horizontally,
	  vertically, and diagonally.

4. **Two More Balls**
	- Adds two extra balls to the play area.
	- Keep as many balls in play as possible to clear bricks faster.

## Features Implemented

- Multiple levels with brick layouts
- Score, lives, paddle growth, and extra-life progression
- Sticky paddle, cannon, explosive ball, and multi-ball power-ups
- Pause, victory, game-over, and high-score states