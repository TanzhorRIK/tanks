import os
import pygame

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
SCREEN_SIZE = [DISPLAY_WIDTH, DISPLAY_HEIGHT]


SPRITE_PLAYER1 = os.path.join("images", "player.png")
SPRITE_ENEMY = os.path.join("images", "enemy.png")
SPRITE_EXPLOSION2 = os.path.join("images", "explosion.png")
SPRITE_BLOCK = os.path.join("images", "block.png")
SPRITE_BLOCKS = os.path.join("images", "blocks.png")
SPRITE_BULLET = os.path.join("images", "bullet.png")

SOUND_SHOT = os.path.join("sounds", "fire.ogg")
SOUND_EXPLOSION = os.path.join("sounds", "explosion.wav")
SOUND_GAMESTART = os.path.join("sounds", "gamestart.ogg")
SOUND_GAMEOVER = os.path.join("sounds", "gameover.ogg")
SOUND_INTRO = os.path.join("sounds", "intro.mp3")
SOUND_GAME = os.path.join("sounds", "music_game.mp3")


LAST_LEVEL = 2
ENEMIES = 3
KILL_GOAL = 10