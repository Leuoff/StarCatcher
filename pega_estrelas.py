# Star Catcher - Pygame Zero
import os
import random
from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.loaders import images

os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

WIDTH = 480
HEIGHT = 640
TITLE = "Star Catcher"

GRAVITY = 0.35
FLAP_STRENGTH = -6.5
PIPE_SPEED = 2.6
PIPE_GAP = 190
PIPE_INTERVAL = 120  # frames
PIPE_WIDTH = 70
BIRD_X = WIDTH // 2
BIRD_SCALE = 0.7

BACKGROUND_IMAGE = "background.png"
BIRD_IMAGE = "et"
STAR_IMAGE = "star"
BACKGROUND_MUSIC = "bg_music"
FLAP_SOUND = "jump"
HIT_SOUND = "hit"

PIPE_COLOR = (60, 200, 90)
PIPE_BORDER = (30, 120, 55)

game_state = "menu"  # "menu", "playing", "game_over"
sound_on = True
score = 0
high_score = 0
pipe_spawn_timer = PIPE_INTERVAL

bird = None
pipes = []

start_button = None
sound_button = None
exit_button = None


class Bird:
    def __init__(self, pos):
        self.actor = Actor(BIRD_IMAGE, pos=pos, anchor=("center", "center"))
        self.actor.scale = BIRD_SCALE
        self.vy = 0

    def flap(self):
        self.vy = FLAP_STRENGTH
        if sound_on:
            getattr(sounds, FLAP_SOUND).play()

    def update(self):
        self.vy += GRAVITY
        self.actor.y += self.vy
        self.actor.angle = max(-30, min(60, -self.vy * 4))

    def draw(self):
        draw_shadow(self.actor, radius=14)
        self.actor.draw()

    @property
    def hitbox(self):
        width = max(8, int(self.actor.width * 0.45))
        height = max(8, int(self.actor.height * 0.55))
        rect = Rect(0, 0, width, height)
        rect.center = (self.actor.x, self.actor.y - 2)
        return rect


class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.star_collected = False
        self.star_actor = Actor(
            STAR_IMAGE,
            pos=(x, gap_y),
            anchor=("center", "center"),
        )
        self.top_rect = Rect((0, 0), (0, 0))
        self.bottom_rect = Rect((0, 0), (0, 0))
        self._update_rects()

    def _update_rects(self):
        half_w = self.width / 2
        gap_half = self.gap / 2

        top_height = max(0, self.gap_y - gap_half)
        self.top_rect = Rect(
            (int(self.x - half_w), 0),
            (int(self.width), int(top_height)),
        )

        bottom_y = self.gap_y + gap_half
        bottom_height = max(0, HEIGHT - bottom_y)
        self.bottom_rect = Rect(
            (int(self.x - half_w), int(bottom_y)),
            (int(self.width), int(bottom_height)),
        )
        self.star_actor.x = self.x
        self.star_actor.y = self.gap_y

    def update(self):
        self.x -= PIPE_SPEED
        self._update_rects()

    def draw(self):
        screen.draw.filled_rect(self.top_rect, PIPE_COLOR)
        screen.draw.rect(self.top_rect, PIPE_BORDER)
        screen.draw.filled_rect(self.bottom_rect, PIPE_COLOR)
        screen.draw.rect(self.bottom_rect, PIPE_BORDER)
        if not self.star_collected:
            self.star_actor.draw()

    @property
    def off_screen(self):
        return self.x + self.width < 0

    @property
    def star_rect(self):
        rect = Rect(0, 0, self.star_actor.width, self.star_actor.height)
        rect.center = (self.star_actor.x, self.star_actor.y)
        return rect


class Button:
    def __init__(self, text, center, width=260, height=50):
        self.text = text
        self.rect = Rect(0, 0, width, height)
        self.rect.center = center

    def draw(self):
        screen.draw.filled_rect(self.rect, (40, 40, 80))
        screen.draw.rect(self.rect, "white")
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontsize=32,
            color="white",
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def init_menu():
    global start_button, sound_button, exit_button

    start_button = Button("Start flight", (WIDTH // 2, HEIGHT // 2 - 40))
    sound_button = Button("Sound: on", (WIDTH // 2, HEIGHT // 2 + 20))
    exit_button = Button("Exit", (WIDTH // 2, HEIGHT // 2 + 80))


def reset_game():
    global bird, pipes, score, pipe_spawn_timer

    bird = Bird((BIRD_X, HEIGHT // 2))
    pipes = []
    score = 0
    pipe_spawn_timer = PIPE_INTERVAL

    if sound_on:
        music.play(BACKGROUND_MUSIC)


def start_game():
    global game_state
    reset_game()
    game_state = "playing"


def go_to_menu():
    global game_state
    game_state = "menu"
    music.stop()


def go_to_game_over():
    global game_state, high_score
    game_state = "game_over"
    music.stop()
    high_score = max(high_score, score)
    if sound_on:
        getattr(sounds, HIT_SOUND).play()


def toggle_sound():
    global sound_on
    sound_on = not sound_on

    if not sound_on:
        music.stop()
    else:
        if game_state == "playing":
            music.play(BACKGROUND_MUSIC)


def spawn_pipe():
    gap_margin = 90
    gap_y = random.randint(gap_margin, HEIGHT - gap_margin)
    pipes.append(Pipe(WIDTH + PIPE_WIDTH, gap_y))


def draw_shadow(actor, radius=14):
    sx = actor.x
    sy = actor.y + 6
    shadow_color = (25, 25, 25)
    screen.draw.filled_circle((sx, sy), radius, shadow_color)


def draw():
    screen.clear()
    draw_background()

    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game()
        draw_game_over_overlay()


def draw_menu():
    screen.draw.text(
        "Star Catcher",
        center=(WIDTH // 2, 120),
        fontsize=64,
        color="yellow",
    )
    screen.draw.text(
        "Tap or press SPACE to flap\nPass through gaps to score",
        center=(WIDTH // 2, 200),
        fontsize=28,
        color="white",
    )

    sound_button.text = f"Sound: {'on' if sound_on else 'off'}"

    start_button.draw()
    sound_button.draw()
    exit_button.draw()

    screen.draw.text(
        "High score: {}".format(high_score),
        center=(WIDTH // 2, HEIGHT - 60),
        fontsize=28,
        color="white",
    )


def draw_game():
    for pipe in pipes:
        pipe.draw()

    if bird:
        bird.draw()

    screen.draw.text(
        f"Score: {score}",
        topleft=(10, 10),
        fontsize=36,
        color="white",
    )
    screen.draw.text(
        f"Best: {high_score}",
        topright=(WIDTH - 10, 10),
        fontsize=28,
        color="white",
    )


def draw_game_over_overlay():
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 140))
    screen.draw.text(
        "Game Over",
        center=(WIDTH // 2, HEIGHT // 2 - 10),
        fontsize=64,
        color="orange",
    )
    screen.draw.text(
        "Score: {}  |  Best: {}".format(score, high_score),
        center=(WIDTH // 2, HEIGHT // 2 + 40),
        fontsize=32,
        color="white",
    )
    screen.draw.text(
        "Press SPACE to retry or ESC to menu",
        center=(WIDTH // 2, HEIGHT // 2 + 90),
        fontsize=28,
        color="white",
    )


def draw_background():
    bg = images.load(BACKGROUND_IMAGE)
    bg_w = max(1, bg.get_width())
    bg_h = max(1, bg.get_height())
    for x in range(0, WIDTH, bg_w):
        for y in range(0, HEIGHT, bg_h):
            screen.blit(BACKGROUND_IMAGE, (x, y))


def update():
    if game_state == "menu":
        update_menu()
    elif game_state == "playing":
        update_game()


def update_menu():
    pass


def update_game():
    global pipe_spawn_timer, score

    bird.update()
    bird_rect = bird.hitbox
    pipe_spawn_timer -= 1
    if pipe_spawn_timer <= 0:
        spawn_pipe()
        pipe_spawn_timer = PIPE_INTERVAL

    for pipe in list(pipes):
        pipe.update()
        if pipe.off_screen:
            pipes.remove(pipe)
            continue

        if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
            go_to_game_over()
            return

        if not pipe.star_collected and pipe.star_rect.colliderect(bird_rect):
            pipe.star_collected = True
            score += 1

    if bird_rect.top < 0 or bird_rect.bottom > HEIGHT - 10:
        go_to_game_over()


def on_mouse_down(pos):
    if game_state == "menu":
        if start_button.is_clicked(pos):
            start_game()
        elif sound_button.is_clicked(pos):
            toggle_sound()
        elif exit_button.is_clicked(pos):
            raise SystemExit
    elif game_state == "playing":
        bird.flap()


def on_key_down(key):
    if game_state == "menu":
        if key == keys.SPACE:
            start_game()
        elif key == keys.ESCAPE:
            raise SystemExit
    elif game_state == "playing":
        if key in (keys.SPACE, keys.UP):
            bird.flap()
        elif key == keys.ESCAPE:
            go_to_menu()
    elif game_state == "game_over":
        if key == keys.SPACE:
            start_game()
        elif key == keys.ESCAPE:
            go_to_menu()


init_menu()
