import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.offset = pygame.math.Vector2(0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height # Stored for potential future use, not directly used in x-scrolling

    def update(self, target_sprite_rect, stage_length):
        # target_sprite_rect is expected to be player.rect
        # Calculate the ideal camera position to center the target
        ideal_x = target_sprite_rect.centerx - self.screen_width / 2

        # Clamp the camera's x position to the stage boundaries
        # Camera's left edge cannot go before stage's left edge (0)
        self.offset.x = max(0, ideal_x)

        # Camera's right edge (offset.x + screen_width) cannot go beyond stage_length
        # So, offset.x cannot be more than stage_length - screen_width
        if stage_length > self.screen_width : # Only clamp if stage is wider than screen
            self.offset.x = min(self.offset.x, stage_length - self.screen_width)
        else: # If stage is narrower than or equal to screen, camera stays at 0
            self.offset.x = 0

        # self.offset.y is not used for horizontal scrolling but could be for vertical
        # For now, it remains 0

    def apply_to_rect(self, rect):
        # Moves a given rect by the inverse of the camera's offset for rendering
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_to_sprite(self, sprite):
        # Returns a new rect for the sprite's position adjusted by the camera
        # Useful for blitting sprites
        return sprite.rect.move(-self.offset.x, -self.offset.y)

    # This method is specifically for the background surface, which might be very wide
    # and whose top-left is always (0,0) in world coordinates.
    def get_background_blit_rect(self, background_surface_rect):
        # background_surface_rect is typically background_surface.get_rect() -> (0,0,width,height)
        # We want to return the rect that should be passed to screen.blit(background_surface, THIS_RECT)
        # This means we need to shift the background's drawing position to the left by offset.x
        return background_surface_rect.move(-self.offset.x, -self.offset.y)
