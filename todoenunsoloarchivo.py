import pygame
import random
import os


class Juego:
    def __init__(self):
        pygame.init()

        # Configuración general
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.LIMITE_INFERIOR_Y = 500
        self.FPS = 60
        self.COLORES = {"blanco": (255, 255, 255), "negro": (0, 0, 0)}

        self.pantalla = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Adventure")

        # Cargar imágenes
        self.fondo = pygame.transform.scale(
            self.cargar_imagen("fondo.jpeg"), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        self.fuente = pygame.font.Font(None, 36)

        # Grupos de sprites
        self.todos_sprites = pygame.sprite.Group()
        self.monedas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Variables de estado
        self.Moneda_contador = 0
        self.ejecutando = True
        self.pausado = False
        self.reloj = pygame.time.Clock()

        # Inicializar elementos del juego
        self.inicializar_elementos()

        # Temporizadores
        self.tiempo_ultimo_goomba_cafe = 0
        self.tiempo_ultimo_goomba_negro = 0
        self.intervalo_cafe = 4000
        self.intervalo_negro = 7000

    def cargar_imagen(self, nombre):
        return pygame.image.load(os.path.join("pictures", nombre)).convert_alpha()

    def inicializar_elementos(self):
        # Jugador
        self.jugador = self.Jugador(self)
        self.todos_sprites.add(self.jugador)

        # Monedas
        for _ in range(10):
            moneda = self.Moneda(self)
            self.monedas.add(moneda)
            self.todos_sprites.add(moneda)

        # Powerups
        self.hongo_crecimiento = self.Hongo(
            self, "crecimiento", 100, self.LIMITE_INFERIOR_Y - 50
        )
        self.hongo_vida = self.Hongo(self, "vida", 700, self.LIMITE_INFERIOR_Y - 50)
        self.estrella = self.Estrella(self, 400, self.LIMITE_INFERIOR_Y - 50)
        self.powerups.add(self.estrella)
        self.todos_sprites.add(self.estrella)

    def iniciar(self):
        # Pantalla inicial
        esperando = True
        while esperando:
            self.pantalla.fill(self.COLORES["negro"])
            texto = self.fuente.render(
                "Presiona ENTER para iniciar", True, self.COLORES["blanco"]
            )
            self.pantalla.blit(
                texto,
                (
                    self.SCREEN_WIDTH // 2 - texto.get_width() // 2,
                    self.SCREEN_HEIGHT // 2,
                ),
            )
            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                    esperando = False

    def game_over(self):
        # Pantalla de game over
        self.ejecutando = False
        game_over = True
        while game_over:
            self.pantalla.fill(self.COLORES["negro"])
            texto1 = self.fuente.render("GAME OVER", True, (255, 0, 0))
            texto2 = self.fuente.render(
                "Presiona R para reiniciar o ESC para salir",
                True,
                self.COLORES["blanco"],
            )
            self.pantalla.blit(
                texto1,
                (
                    self.SCREEN_WIDTH // 2 - texto1.get_width() // 2,
                    self.SCREEN_HEIGHT // 2 - 40,
                ),
            )
            self.pantalla.blit(
                texto2,
                (
                    self.SCREEN_WIDTH // 2 - texto2.get_width() // 2,
                    self.SCREEN_HEIGHT // 2 + 20,
                ),
            )
            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.salir()
                    elif evento.key == pygame.K_r:
                        game_over = False
                        self.resetear_juego()

    def resetear_juego(self):
        # Reiniciar estado del juego
        self.ejecutando = True
        self.todos_sprites.empty()
        self.monedas.empty()
        self.enemigos.empty()
        self.powerups.empty()
        self.Moneda_contador = 0
        self.inicializar_elementos()

    def salir(self):
        pygame.quit()
        exit()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.salir()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:  # Pausa con tecla P
                    self.pausado = not self.pausado
                if evento.key == pygame.K_r and not self.ejecutando:
                    self.resetear_juego()

    def actualizar_enemigos(self, tiempo_actual):
        # Generación de enemigos
        if len(self.enemigos) < 2:
            if tiempo_actual - self.tiempo_ultimo_goomba_cafe > self.intervalo_cafe:
                enemigo = self.Enemigo(self, "cafe")
                self.enemigos.add(enemigo)
                self.todos_sprites.add(enemigo)
                self.tiempo_ultimo_goomba_cafe = tiempo_actual

            if tiempo_actual - self.tiempo_ultimo_goomba_negro > self.intervalo_negro:
                enemigo = self.Enemigo(self, "negro")
                self.enemigos.add(enemigo)
                self.todos_sprites.add(enemigo)
                self.tiempo_ultimo_goomba_negro = tiempo_actual

    def manejar_colisiones(self):
        # Colisiones con monedas
        for moneda in pygame.sprite.spritecollide(self.jugador, self.monedas, True):
            self.Moneda_contador += 1
            if self.Moneda_contador >= 10:
                self.jugador.vidas += 1
                self.Moneda_contador = 0
            moneda.resetear_posicion()
            self.monedas.add(moneda)
            self.todos_sprites.add(moneda)

        # Colisiones con powerups
        for powerup in pygame.sprite.spritecollide(self.jugador, self.powerups, False):
            if isinstance(powerup, self.Hongo) and powerup.visible:
                powerup.recolectar()
                if powerup.tipo == "crecimiento":
                    self.jugador.estado = "grande"
                    self.jugador.actualizar_tamano()
                else:
                    self.jugador.vidas += 1
            elif isinstance(powerup, self.Estrella) and powerup.visible:
                self.jugador.estado = "inmune"
                self.jugador.tiempo_inmunidad = (
                    pygame.time.get_ticks() + powerup.duracion
                )
                powerup.recolectar()

        # Colisiones con enemigos
        if self.jugador.vidas > 0:  # Solo detectar colisiones si está vivo
            for enemigo in pygame.sprite.spritecollide(
                self.jugador, self.enemigos, False
            ):
                if self.jugador.estado != "inmune":
                    if self.jugador.estado == "grande":
                        self.jugador.estado = "pequeño"
                        self.jugador.actualizar_tamano()
                        enemigo.kill()
                    else:
                        self.jugador.vidas -= 1
                        if self.jugador.vidas <= 0:
                            self.game_over()
                            return  # Salir del método para evitar actualizaciones
                        else:
                            self.jugador.rect.topleft = (
                                100,
                                self.LIMITE_INFERIOR_Y - 50,
                            )

    def manejar_reaparicion_objetos(self, tiempo_actual):
        # Reaparición de hongos
        for hongo in [self.hongo_crecimiento, self.hongo_vida]:
            if not hongo.visible and tiempo_actual > hongo.tiempo_reaparicion:
                hongo.aparecer()

        # Reaparición de estrella
        if (
            not self.estrella.visible
            and tiempo_actual > self.estrella.tiempo_reaparicion
        ):
            self.estrella.aparecer()

    def bucle_principal(self):
        self.ejecutando = True
        while self.ejecutando:
            self.reloj.tick(self.FPS)
            tiempo_actual = pygame.time.get_ticks()

            self.manejar_eventos()

            if not self.pausado:
                # Actualizar lógica del juego
                self.actualizar_enemigos(tiempo_actual)
                self.todos_sprites.update()
                self.manejar_colisiones()
                self.manejar_reaparicion_objetos(tiempo_actual)

                # Dibujado
                self.pantalla.blit(self.fondo, (0, 0))
                self.todos_sprites.draw(self.pantalla)

                # HUD
                texto_vidas = self.fuente.render(
                    f"Vidas: {self.jugador.vidas}", True, self.COLORES["blanco"]
                )
                texto_monedas = self.fuente.render(
                    f"Monedas: {self.Moneda_contador}/10", True, self.COLORES["blanco"]
                )
                self.pantalla.blit(texto_vidas, (10, 10))
                self.pantalla.blit(texto_monedas, (10, 50))
                # Mostrar tiempo de inmunidad
                if self.jugador.estado == "inmune":
                    tiempo_restante = max(
                        0, (self.jugador.tiempo_inmunidad - tiempo_actual) // 1000
                    )
                    texto_inmune = self.fuente.render(
                        f"Inmune: {tiempo_restante}s", True, (255, 255, 0)
                    )
                    self.pantalla.blit(texto_inmune, (10, 90))

                # Mostrar pausa
                if self.pausado:
                    texto_pausa = self.fuente.render(
                        "PAUSA - Presiona P para continuar", True, (255, 0, 0)
                    )
                    self.pantalla.blit(
                        texto_pausa,
                        (
                            self.SCREEN_WIDTH // 2 - texto_pausa.get_width() // 2,
                            self.SCREEN_HEIGHT // 2,
                        ),
                    )

            pygame.display.flip()

    # Clases internas
    class Jugador(pygame.sprite.Sprite):
        def __init__(self, juego):
            super().__init__()
            self.juego = juego
            self.imagen_original = juego.cargar_imagen("player.png")
            self.imagen_salto = juego.cargar_imagen("player_salto.png")
            self.image = pygame.transform.scale(self.imagen_original, (50, 50))
            self.rect = self.image.get_rect(topleft=(100, juego.LIMITE_INFERIOR_Y - 50))
            self.vidas = 3
            self.estado = "pequeño"
            self.tiempo_inmunidad = 0
            self.velocidad = 5
            self.vel_y = 0
            self.en_suelo = True
            self.salto_potencia = -15
            self.gravedad = 1

        def actualizar_tamano(self):
            nuevo_tamano = (60, 60) if self.estado == "grande" else (50, 50)
            self.image = pygame.transform.scale(self.imagen_original, nuevo_tamano)

        def update(self):
            teclas = pygame.key.get_pressed()
            dx = 0

            if teclas[pygame.K_LEFT]:
                dx -= self.velocidad
            if teclas[pygame.K_RIGHT]:
                dx += self.velocidad

            nueva_x = self.rect.x + dx
            if nueva_x < 0:
                nueva_x = 0
            elif nueva_x > self.juego.SCREEN_WIDTH - self.rect.width:
                nueva_x = self.juego.SCREEN_WIDTH - self.rect.width
            self.rect.x = nueva_x

            # Saltar
            if teclas[pygame.K_SPACE] and self.en_suelo:
                self.vel_y = self.salto_potencia
                self.en_suelo = False
                self.cambiar_imagen_salto()

            self.vel_y += self.gravedad
            self.rect.y += self.vel_y

            # Colisión con el suelo
            if self.rect.bottom >= self.juego.LIMITE_INFERIOR_Y:
                self.rect.bottom = self.juego.LIMITE_INFERIOR_Y
                self.vel_y = 0
                if not self.en_suelo:
                    self.en_suelo = True
                    self.cambiar_imagen_normal()

            # Fin de inmunidad
            if (
                self.estado == "inmune"
                and pygame.time.get_ticks() > self.tiempo_inmunidad
            ):
                # Volver al estado anterior (grande o pequeño)
                self.estado = "grande" if self.image.get_size()[0] == 60 else "pequeño"
                self.actualizar_tamano()

        def cambiar_imagen_salto(self):
            nuevo_tamano = (60, 60) if self.estado == "grande" else (50, 50)
            self.image = pygame.transform.scale(self.imagen_salto, nuevo_tamano)

        def cambiar_imagen_normal(self):
            nuevo_tamano = (60, 60) if self.estado == "grande" else (50, 50)
            self.image = pygame.transform.scale(self.imagen_original, nuevo_tamano)

    class Moneda(pygame.sprite.Sprite):
        def __init__(self, juego):
            super().__init__()
            self.juego = juego
            self.image = pygame.transform.scale(
                juego.cargar_imagen("coin.png"), (30, 30)
            )
            self.rect = self.image.get_rect()
            self.resetear_posicion()

        def resetear_posicion(self):
            self.rect.x = random.randint(0, self.juego.SCREEN_WIDTH - 30)
            self.rect.y = random.randint(
                self.juego.LIMITE_INFERIOR_Y - 150, self.juego.LIMITE_INFERIOR_Y - 30
            )

    class Hongo(pygame.sprite.Sprite):
        def __init__(self, juego, tipo, x, y):
            super().__init__()
            self.juego = juego
            self.tipo = tipo
            self.image = pygame.transform.scale(
                juego.cargar_imagen(
                    "hongo.png" if tipo == "crecimiento" else "vida.png"
                ),
                (40, 40),
            )
            self.rect = self.image.get_rect(topleft=(x, y))
            self.visible = False
            self.tiempo_reaparicion = 0

        def aparecer(self):
            self.visible = True
            self.rect.topleft = (
                random.randint(50, self.juego.SCREEN_WIDTH - 50),
                random.randint(
                    self.juego.LIMITE_INFERIOR_Y - 150,
                    self.juego.LIMITE_INFERIOR_Y - 50,
                ),
            )
            self.juego.powerups.add(self)
            self.juego.todos_sprites.add(self)

        def recolectar(self):
            self.visible = False
            self.tiempo_reaparicion = pygame.time.get_ticks() + 5000
            self.juego.powerups.remove(self)
            self.juego.todos_sprites.remove(self)

    class Estrella(pygame.sprite.Sprite):
        def __init__(self, juego, x, y):
            super().__init__()
            self.juego = juego
            self.image = pygame.transform.scale(
                juego.cargar_imagen("estrella.png"), (40, 40)
            )
            self.rect = self.image.get_rect(topleft=(x, y))
            self.duracion = 8000
            self.visible = True
            self.tiempo_reaparicion = 0

        def aparecer(self):
            self.visible = True
            self.rect.topleft = (
                random.randint(50, self.juego.SCREEN_WIDTH - 50),
                random.randint(
                    self.juego.LIMITE_INFERIOR_Y - 150,
                    self.juego.LIMITE_INFERIOR_Y - 50,
                ),
            )
            self.juego.powerups.add(self)
            self.juego.todos_sprites.add(self)
            self.tiempo_reaparicion = pygame.time.get_ticks() + 10000

        def recolectar(self):
            self.visible = False
            self.tiempo_reaparicion = pygame.time.get_ticks() + 10000
            self.juego.powerups.remove(self)
            self.juego.todos_sprites.remove(self)

    class Enemigo(pygame.sprite.Sprite):
        def __init__(self, juego, tipo):
            super().__init__()
            self.juego = juego
            self.tipo = tipo
            self.image = pygame.transform.scale(
                juego.cargar_imagen(f"goomba_{tipo}.png"), (40, 40)
            )
            self.rect = self.image.get_rect(
                topleft=(juego.SCREEN_WIDTH, juego.LIMITE_INFERIOR_Y - 40)
            )
            self.velocidad = 3 if tipo == "cafe" else 5

        def update(self):
            self.rect.x -= self.velocidad
            if self.rect.right < 0:
                self.kill()


juego = Juego()
while True:
    juego.iniciar()
    juego.bucle_principal()
