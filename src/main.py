import sys

import pygame
import numpy as np

MAX_SCORE = 11
FPS = 60
BLACK = (0, 0, 0)
COLOR_A = (255, 23, 23)
COLOR_B = (23, 23, 255)
WHITE = (255, 255, 255)
PDL_WIDTH = 10
PDL_HEIGHT = 100
SCREEN_WIDTH = 840
SCREEN_HEIGHT = 600
PDL_SPEED = 10
RADIUS = 10
SIMPLE_AI_SPEED = 7

pygame.init()
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Pong")

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)


def quit_game():
    pygame.quit()
    sys.exit()


class Ball(pygame.sprite.Sprite):

    def __init__(self, color, width, height, radius):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.RADIUS = radius
        self.width = width
        self.height = height
        self.velocity = [np.random.randint(2, 5), np.random.randint(-4, 5)]

        pygame.draw.circle(self.image, color, (self.width // 2, self.height // 2), self.RADIUS)

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]

    def bounce(self):
        self.velocity[0] = -self.velocity[0]
        self.velocity[1] = np.random.uniform(-4, 5)


class Paddle(pygame.sprite.Sprite):

    def __init__(self, color, width, height, name):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.width = width
        self.height = height
        self.name = name

        pygame.draw.rect(self.image, color, [0, 0, self.width, self.height])
        self.rect = self.image.get_rect()

    def move_up(self, pixels):
        self.rect.y -= pixels
        if self.rect.y < 0:
            self.rect.y = 0

    def move_down(self, pixels):
        self.rect.y += pixels
        if self.rect.y > (SCREEN_HEIGHT - self.height):
            self.rect.y = (SCREEN_HEIGHT - self.height)

    def simple_ai(self, ball_pos_y, pixels):
        if ball_pos_y + RADIUS > self.rect.y + PDL_HEIGHT / 2:
            self.rect.y += pixels
        if ball_pos_y + RADIUS < self.rect.y + PDL_HEIGHT / 2:
            self.rect.y -= pixels

        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > (SCREEN_HEIGHT - self.height):
            self.rect.y = (SCREEN_HEIGHT - self.height)


class Game:
    def __init__(self, player_a, player_b, ball):

        self.state = None
        pygame.init()

        self.paddle_a = player_a
        self.paddle_a.rect.x = 0
        self.paddle_a.rect.y = (SCREEN_HEIGHT - PDL_HEIGHT) // 2

        self.paddle_b = player_b
        self.paddle_b.rect.x = SCREEN_WIDTH - PDL_WIDTH
        self.paddle_b.rect.y = (SCREEN_HEIGHT - PDL_HEIGHT) // 2

        self.ball = ball

        self.all_sprites_list = pygame.sprite.Group()
        self.all_sprites_list.add(self.paddle_a, self.paddle_b, self.ball)

        self.clock = pygame.time.Clock()

        self.score_a, self.score_b = 0, 0
        self.reward = 0

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu()

            self.paddle_b.simple_ai(self.ball.rect.y, SIMPLE_AI_SPEED)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.paddle_a.move_up(PDL_SPEED)
            if keys[pygame.K_DOWN]:
                self.paddle_a.move_down(PDL_SPEED)

            self.ball.update()
            paddle_group = pygame.sprite.Group(self.paddle_a, self.paddle_b)
            if pygame.sprite.spritecollide(self.ball, paddle_group, False):
                self.ball.bounce()

            if self.ball.rect.x > SCREEN_WIDTH:
                (self.ball.rect.x, self.ball.rect.y) = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.ball.velocity[0] *= -1
                self.score_a += 1
            elif self.ball.rect.x < 0:
                (self.ball.rect.x, self.ball.rect.y) = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.ball.velocity[0] *= -1
                self.score_b += 1

            if self.ball.rect.y > SCREEN_HEIGHT - 2 * RADIUS:
                self.ball.velocity[1] *= -1
            if self.ball.rect.y < 0:
                self.ball.velocity[1] *= -1

            screen.fill(BLACK)
            pygame.draw.line(screen, WHITE, [SCREEN_WIDTH // 2, 0], [SCREEN_WIDTH // 2, SCREEN_HEIGHT], 5)
            self.all_sprites_list.draw(screen)

            font = pygame.font.Font(None, 74)
            text = font.render(str(self.score_a), 1, COLOR_A)
            screen.blit(text, (SCREEN_WIDTH // 4, 10))
            text = font.render(str(self.score_b), 1, COLOR_B)
            screen.blit(text, (3 * SCREEN_WIDTH // 4, 10))

            self.all_sprites_list.update()

            pygame.display.flip()
            self.clock.tick(FPS)

            if self.score_a == MAX_SCORE or self.score_b == MAX_SCORE:
                main_menu()


def game():
    player_a = Paddle(COLOR_A, PDL_WIDTH, PDL_HEIGHT, "A")
    player_b = Paddle(COLOR_B, PDL_WIDTH, PDL_HEIGHT, "B")
    ball = Ball(WHITE, 2 * RADIUS, 2 * RADIUS, RADIUS)
    g = Game(player_a, player_b, ball)
    g.play()


def main_menu():
    buttons = []
    button_width = 200
    button_height = 50
    button_left = SCREEN_WIDTH // 2 - button_width // 2
    button_top = 200
    button_play = pygame.Rect(button_left, button_top, button_width, button_height)
    button_exit = pygame.Rect(button_left, button_top + 200, button_width, button_height)
    buttons.append((button_play, (0, 0, 155)))
    buttons.append((button_exit, (155, 0, 0)))

    while True:
        screen.fill(BLACK)
        text_play = font_small.render("Play", True, (255, 255, 255))
        text_exit = font_small.render("Exit", True, (255, 255, 255))
        mx, my = pygame.mouse.get_pos()

        for button in buttons:
            pygame.draw.rect(screen, button[1], button[0])

        screen.blit(text_play,
                    text_play.get_rect(center=(button_left + button_width // 2, button_top + button_height // 2)))
        screen.blit(text_exit,
                    text_exit.get_rect(center=(button_left + button_width // 2, button_top + 200 + button_height // 2)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    game()
                if button_exit.collidepoint(mx, my):
                    quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if event.key == pygame.K_g:
                    game()
        pygame.display.update()


if __name__ == "__main__":
    main_menu()
