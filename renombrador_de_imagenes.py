import os
import sys
import pygame
from pygame.locals import *

pygame.init()

# Configuración de colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
LIGHT_GREY = (220, 220, 220)
BLUE = (0, 0, 255)

# Configuración de la ventana
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Renombrador de Imágenes')

# Fuente
font = pygame.font.Font(None, 32)

# Input de texto
input_box = pygame.Rect(100, 50, 200, 32)
input_text = ""
input_surface = font.render(input_text, True, BLACK)

# Botón de cambio de nombre
button_text = "Cambiar nombre"
button_surface = font.render(button_text, True, BLACK)
button_width = button_surface.get_width() + 20
button = pygame.Rect(100, 250, button_width, 32)

# Rectángulo de arrastrar y soltar
drop_rect = pygame.Rect(50, 100, 300, 100)
drop_rect_text = "No hay imágenes cargadas"
drop_rect_surface = font.render(drop_rect_text, True, BLACK)

# Lista de archivos
files = []

def draw_drop_rect_text(text):
    words = text.split()
    lines = ['']
    for word in words:
        temp_line = lines[-1] + ' ' + word if lines[-1] else word
        if font.size(temp_line)[0] <= drop_rect.width - 20:
            lines[-1] = temp_line
        else:
            lines.append(word)

    for i, line in enumerate(lines):
        line_surface = font.render(line.strip(), True, BLACK)
        screen.blit(line_surface, (drop_rect.x + drop_rect.width // 2 - line_surface.get_width() // 2,
                                   drop_rect.y + drop_rect.height // 2 - font.get_linesize() * (len(lines) - i * 2) // 2))

def rename_files(files, new_name_base):
    renamed_files = []
    for i, file in enumerate(files, 1):
        file_path, extension = os.path.splitext(file)
        if extension.lower() in [".jpg", ".png"]:
            new_name = f"{new_name_base}{i}.png"
            new_file_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file, new_file_path)
            renamed_files.append(new_file_path)
    return len(renamed_files)

def adjust_input_box(text):
    lines = text.splitlines()
    if not lines:  # Si la secuencia de líneas está vacía, establece el ancho y alto predeterminados
        input_box.width = 200
        input_box.height = 32
    else:
        max_width = WIDTH - 20  # Ajusta el ancho máximo para evitar que el texto se salga de los límites de la ventana
        new_lines = []
        for line in lines:
            while font.size(line)[0] > max_width:
                split_index = len(line)
                while split_index > 0 and font.size(line[:split_index])[0] > max_width:
                    split_index -= 1
                new_lines.append(line[:split_index].strip())
                line = line[split_index:].strip()
            new_lines.append(line)
        lines = new_lines
        text = "\n".join(lines)

        width = max(font.size(line)[0] for line in lines)
        height = len(lines) * font.get_linesize() * 1.2 # Aumenta el espacio entre las líneas en un 20%
        input_box.width = max(200, width + 10)
        input_box.height = max(32, height + 10)
        input_box.x = WIDTH // 2 - input_box.width // 2

    return text


active = False
running = True

# Puntero parpadeante
blink_start_time = 0
blink_interval = 500  # en milisegundos

while running:
    screen.fill(WHITE)
    

    # Ajustar el tamaño de la ventana si el cuadro de entrada de texto ocupa demasiado espacio
    if input_box.y + input_box.height + button.height + drop_rect.height + 40 > HEIGHT:
        HEIGHT = input_box.y + input_box.height + button.height + drop_rect.height + 40
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == K_RETURN:
                input_text += '\n'
            else:
                input_text += event.unicode
            input_text = adjust_input_box(input_text)
            input_surface = font.render(input_text, True, BLACK)

        if event.type == MOUSEBUTTONDOWN:
            if button.collidepoint(event.pos) and input_text and files:
                renamed_count = rename_files(files, input_text)
                if renamed_count == 1:
                    drop_rect_text = "1 imagen renombrada con éxito"
                else:
                    drop_rect_text = f"{renamed_count} imágenes renombradas con éxito"
                drop_rect_surface = font.render(drop_rect_text, True, BLACK)
                files = []


            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False

        if event.type == DROPFILE:
            files.append(event.file)
            drop_rect_text = f"{len(files)} imágenes cargadas"
            drop_rect_surface = font.render(drop_rect_text, True, BLACK)

    # Dibuja el rectángulo de arrastrar y soltar
    drop_rect.y = input_box.y + input_box.height + 20
    pygame.draw.rect(screen, LIGHT_GREY, drop_rect, 2)
    draw_drop_rect_text(drop_rect_text)


    # Dibuja el cuadro de entrada de texto
    pygame.draw.rect(screen, GREY, input_box)
    input_box_centery = input_box.y + input_box.height // 2
    lines = input_text.splitlines()
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, BLACK)
        screen.blit(line_surface, (input_box.x + 5, input_box_centery - font.get_linesize() * (len(lines) - i) // 2))

    # Dibuja el puntero parpadeante
    if active:
        elapsed_time = pygame.time.get_ticks() - blink_start_time
        if elapsed_time % (blink_interval * 2) < blink_interval:
            last_line = lines[-1] if lines else ""
            cursor_x = input_box.x + font.size(last_line)[0] + 5
            cursor_y = input_box_centery - font.get_linesize() * (len(lines) - len(lines)) // 2
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_linesize()), 2)

    # Cambia el color del botón según si se ha escrito algo en el cuadro de entrada y si hay imágenes cargadas
    button.y = drop_rect.y + drop_rect.height + 20
    if input_text and files:
        pygame.draw.rect(screen, BLUE, button)
    else:
        pygame.draw.rect(screen, GREY, button)
    screen.blit(button_surface, (button.x + 10, button.y + 5))

    pygame.display.flip()

pygame.quit()
