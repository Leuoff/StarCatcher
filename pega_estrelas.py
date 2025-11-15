import random
from pgzero.actor import Actor

# Tamanho da janela
WIDTH = 800
HEIGHT = 600

# Ator do jogador (imagem: player.png, na pasta images/)
player = Actor("player")
player.pos = (WIDTH // 2, HEIGHT - 70)

# Ator da estrela (imagem: star.png)
star = Actor("star")
star.pos = (random.randint(40, WIDTH - 40), -40)

# Variáveis do jogo
score = 0
vidas = 3
velocidade_estrela = 3
game_over = False


def draw():
    screen.clear()

    # fundo simples
    screen.fill((15, 15, 40))  # azul escuro / espaço

    # desenha jogador e estrela
    player.draw()
    star.draw()

    # placar
    screen.draw.text(f"Pontos: {score}", topleft=(10, 10),
                     fontsize=32, color="white")
    screen.draw.text(f"Vidas: {vidas}", topright=(WIDTH - 10, 10),
                     fontsize=32, color="white")

    if game_over:
        screen.draw.text("FIM DE JOGO", center=(WIDTH // 2, HEIGHT // 2 - 20),
                         fontsize=72, color="yellow")
        screen.draw.text("Pressione ESPACO para recomecar",
                         center=(WIDTH // 2, HEIGHT // 2 + 40),
                         fontsize=32, color="white")


def update():
    global score, vidas, velocidade_estrela, game_over

    # se o jogo acabou, não atualiza o resto
    if game_over:
        return

    # mover jogador
    if keyboard.left:
        player.x -= 5
    if keyboard.right:
        player.x += 5

    # impedir que saia da tela
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH

    # mover estrela
    star.y += velocidade_estrela

    # estrela saiu da tela sem ser pega
    if star.top > HEIGHT:
        vidas -= 1
        resetar_estrela()

        if vidas <= 0:
            game_over = True

    # verificar colisão jogador x estrela
    if player.colliderect(star):
        score += 1
        # deixa o jogo um pouquinho mais difícil
        velocidade_estrela += 0.2
        resetar_estrela()


def resetar_estrela():
    """Coloca a estrela lá em cima, em posição aleatória."""
    star.x = random.randint(40, WIDTH - 40)
    star.y = -40


def on_key_down(key):
    global score, vidas, velocidade_estrela, game_over

    # Se o jogo terminou, espaço reinicia
    if game_over and key == keys.SPACE:
        score = 0
        vidas = 3
        velocidade_estrela = 3
        resetar_estrela()
        game_over = False
