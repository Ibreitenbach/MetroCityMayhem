import pygame

import random

class Camera:
    def __init__(self, screen_width, screen_height):
        self.offset = pygame.math.Vector2(0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Screen Shake Attributes
        self.shake_intensity = 0
        self.shake_timer = 0.0
        self.shake_duration = 0.0

    def start_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration # Start the timer

    def update(self, target_sprite_rect, stage_length, dt): # Added dt for shake timer
        # Calculate the ideal camera position to center the target
        ideal_x = target_sprite_rect.centerx - self.screen_width / 2

        # Base offset calculation (clamped)
        calculated_offset_x = max(0, ideal_x)
        if stage_length > self.screen_width:
            calculated_offset_x = min(calculated_offset_x, stage_length - self.screen_width)
        else:
            calculated_offset_x = 0

        self.offset.x = calculated_offset_x
        self.offset.y = 0 # Assuming no vertical scrolling for now

        # Apply screen shake if active
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer > 0:
                shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                # shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity) # Optional vertical shake
                self.offset.x += shake_offset_x
                # self.offset.y += shake_offset_y

                # Re-clamp after shake to ensure it doesn't push view outside stage boundaries
                self.offset.x = max(0, self.offset.x)
                if stage_length > self.screen_width:
                     self.offset.x = min(self.offset.x, stage_length - self.screen_width)
                else: # If stage is narrower, camera stays at 0 even with shake
                    self.offset.x = 0

            else: # Shake timer just expired
                self.shake_intensity = 0
                # self.offset.x is already set to calculated_offset_x from the start of this frame,
                # so no need to "reset" it explicitly here, as the shake is additive for the current frame only.

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
