import pygame

class DialogueBox:
    def __init__(self, screen_width, screen_height, font=None, padding=20, line_spacing=5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font if font else pygame.font.Font(None, 28) # Default font
        self.padding = padding
        self.line_spacing = line_spacing

        self.box_height = 150 # Example height
        self.box_rect = pygame.Rect(
            self.padding,
            self.screen_height - self.box_height - self.padding,
            self.screen_width - (2 * self.padding),
            self.box_height
        )
        self.text_area_rect = pygame.Rect(
            self.box_rect.x + self.padding,
            self.box_rect.y + self.padding,
            self.box_rect.width - (2 * self.padding),
            self.box_rect.height - (2 * self.padding)
        )

        self.background_color = pygame.Color('black')
        self.border_color = pygame.Color('white')
        self.text_color = pygame.Color('white')
        self.name_color = pygame.Color('yellow')

        self.is_showing = False
        self.current_dialogue_lines = []
        self.current_character_name = ""
        self.current_line_index = 0 # For multi-page dialogues
        self.max_lines_per_page = 3 # How many lines fit in the box at once (approx)

    def _wrap_text(self, text, max_width):
        words = text.split(' ')
        wrapped_lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            # Use font.size to check width, not rendering the whole surface repeatedly
            text_width, _ = self.font.size(test_line)
            if text_width <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "
        wrapped_lines.append(current_line.strip())
        return wrapped_lines

    def start_dialogue(self, character_name, dialogue_content): # dialogue_content can be a list of lines or one long string
        self.current_character_name = character_name

        if isinstance(dialogue_content, str):
            self.current_dialogue_lines = self._wrap_text(dialogue_content, self.text_area_rect.width)
        elif isinstance(dialogue_content, list):
            wrapped_content = []
            for line in dialogue_content:
                wrapped_content.extend(self._wrap_text(line, self.text_area_rect.width))
            self.current_dialogue_lines = wrapped_content
        else:
            self.current_dialogue_lines = ["Error: Invalid dialogue content."]

        self.current_line_index = 0
        self.is_showing = True
        # print(f"Dialogue started. Name: {self.current_character_name}, Lines: {self.current_dialogue_lines}")

    def next_page(self):
        if self.current_line_index + self.max_lines_per_page < len(self.current_dialogue_lines):
            self.current_line_index += self.max_lines_per_page
            # print(f"Dialogue next page. Index: {self.current_line_index}")
            return True # More pages exist
        else:
            self.end_dialogue()
            return False # No more pages, dialogue ended

    def end_dialogue(self):
        self.is_showing = False
        self.current_dialogue_lines = []
        self.current_character_name = ""
        self.current_line_index = 0
        # print("Dialogue ended.")

    def draw(self, surface):
        if not self.is_showing:
            return

        pygame.draw.rect(surface, self.background_color, self.box_rect)
        pygame.draw.rect(surface, self.border_color, self.box_rect, 2)

        name_y_pos = self.text_area_rect.y
        if self.current_character_name:
            name_surface = self.font.render(self.current_character_name, True, self.name_color)
            # Position name inside the box, above the first line of text
            name_render_pos = (self.text_area_rect.x, self.text_area_rect.y)
            surface.blit(name_surface, name_render_pos)
            name_y_pos += name_surface.get_height() + self.line_spacing # Adjust y_offset for text below name

        lines_to_display = self.current_dialogue_lines[self.current_line_index : self.current_line_index + self.max_lines_per_page]

        for i, line in enumerate(lines_to_display):
            line_surface = self.font.render(line, True, self.text_color)
            surface.blit(line_surface, (self.text_area_rect.x, name_y_pos + (i * (self.font.get_linesize() + self.line_spacing))))

        hint_text = self.font.render("Press Enter...", True, self.text_color) # Simplified hint
        hint_rect = hint_text.get_rect(right=self.box_rect.right - self.padding, bottom=self.box_rect.bottom - self.padding / 2)
        surface.blit(hint_text, hint_rect)
