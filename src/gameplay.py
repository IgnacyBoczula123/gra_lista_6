import pygame
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_QUIT = "quit"
STATE_PAUSE   = "pause"

DIFFICULTY_SPEED = {
    'easy':   8,
    'normal': 10,
    'hard':   12,
}

# 1. Inicjalizacja
def game_loop(difficulty):

    from klasa import Player, Clouds
    from funkcje import draw_text, draw_rocks, update_highscores, draw_centered_text
    from screens_def import Pause_loop 
    from path_func import Load_graphics

    pygame.init()
    WIDTH, HEIGHT = 1300, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jumping Franek")
    clock = pygame.time.Clock()

    # — wczytania grafik robimy tylko raz, przed pętlą restartów —
    bg_img = pygame.image.load(Load_graphics("background.jpg")).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    ground_img = pygame.image.load(Load_graphics("ground.png")).convert_alpha()
    ground_width = ground_img.get_width()

    # Pętla restartów – dzięki niej przy każdym „reset” gra zaczyna się od nowa
    while True:
        # 1) (Re)inicjalizacja stanu gry
        x_offset     = 0
        ground_speed = DIFFICULTY_SPEED.get(difficulty, 10)
        points       = 0
        points_speed = 100 ** (ground_speed/10)

        player        = Player(x=400, y=720)
        initial_positions = (1000,1700,2700,4500,5300,5960,6500,7260,7900,8670,9600)
        initial_nums      = (1,1,2,1,1,2,2,2,1,2,1)
        rocks_group = draw_rocks(initial_positions,
                                 initial_nums,
                                 speed=ground_speed)
        rocks_list  = rocks_group.sprites()
        clouds = [
            Clouds(1, pos=(1200,250), speed=2),
            Clouds(1, pos=(2300,200), speed=2.5),
            Clouds(2, pos=(2000,220), speed=2)
        ]
        all_sprites = pygame.sprite.Group(player, *clouds, *rocks_list)
        rocks       = pygame.sprite.Group(*rocks_list)

        # 2) Właściwa rozgrywka — trwa aż do kolizji
        while True:
            dt = clock.tick(60) / 1000.0
            points += points_speed * dt

            # a) eventy
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return STATE_QUIT
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    next_state = Pause_loop()
                    if next_state != STATE_PLAYING:
                        return next_state

            # b) update
            all_sprites.update()

            # c) sprawdzenie kolizji → koniec gry
            if pygame.sprite.spritecollide(player, rocks, False, pygame.sprite.collide_mask):
                update_highscores(score=points)
                break  # wyjdź do ekranu GAME OVER

            # d) przesuwanie podłoża, odświeżanie skał itp.
            x_offset -= ground_speed
            if x_offset <= -ground_width:
                x_offset += ground_width

            if all(r.rect.right < 100 for r in rocks_list):
                # … generowanie nowych skał jak wcześniej …
                ground_speed += 2
                

                spawn_base =  WIDTH -100
                rels = [p - initial_positions[0] for p in initial_positions]

                # stwórz nowy segment
                new_positions = tuple(spawn_base + r for r in rels)
                new_group = draw_rocks(new_positions,
                                    initial_nums,
                                    speed=ground_speed)
                rocks_list = new_group.sprites()

                # dodaj je z powrotem
                all_sprites.add(*rocks_list)
                rocks.add(*rocks_list)

            # e) rysowanie
            screen.blit(bg_img, (0,0))
            screen.blit(ground_img, (x_offset, -150))
            screen.blit(ground_img, (x_offset + ground_width - 120, -150))
            all_sprites.draw(screen)
            draw_text(screen, f"PUNKTY:  {int(points)}", pos=(50,90), center=False)
            draw_text(screen, f"Poziom:  {difficulty}", pos=(50,150), center=False)
            draw_text(screen, "ESC: Pauza", pos=(50, 20), center=False,size=32)
            pygame.display.flip()

        # 3) Ekran GAME OVER – komunikat i oczekiwanie na SPACJĘ
        waiting = True
        while waiting:
            # Możesz pokazać ostatnią klatkę, albo czarne tło:
            screen.blit(bg_img, (0,0))
            lines = [f"GAME OVER Wynik: {int(points)}",
                    "Naciśnij ENTER, aby grać dalej",
                    "Naciśnij ESC, aby wyjść do MENU"]
            draw_centered_text(screen,lines, center_x =WIDTH//2, center_y = HEIGHT//2 - 50 )
            pygame.display.flip()
            clock.tick(60)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return STATE_QUIT
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        waiting = False   # wyjdź i zrestartuj grę
                    elif e.key == pygame.K_ESCAPE:
                        return STATE_MENU  # powrót do menu głównego

        
                  


