import pygame
import random
from head_controls import HeadController

# Button class for creating interactive buttons
class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        # Change button color on hover
        pygame.draw.rect(screen, self.hover_color if is_hovered else self.color, self.rect)

        # Draw button text
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 512))  # Screen size
        self.clock = pygame.time.Clock()

        # Load game assets
        self.bird = pygame.image.load('../assets/bird.png').convert_alpha()
        self.background = pygame.image.load('../assets/background.png').convert_alpha()
        self.pipe_surface1 = pygame.image.load('../assets/pipe1.png').convert_alpha()  # Top pipe
        self.pipe_surface2 = pygame.image.load('../assets/pipe2.png').convert_alpha()  # Bottom pipe
        self.bird_y = 250  # Initial bird position
        self.bird_movement = 0
        self.gravity = 0.25

        # Head controller for controlling the bird
        self.head_controller = HeadController()

        # Pipe variables
        self.pipe_list = []
        self.pipe_height = [200, 300, 400]  # Different heights for pipes
        self.pipe_spawn_time = pygame.USEREVENT
        pygame.time.set_timer(self.pipe_spawn_time, 2800)  # Spawn pipes every 2.8 seconds

        self.pipe_gap = 200  # Vertical gap between top and bottom pipes

        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 40)

        # Game state
        self.game_active = True
        self.paused = False

        # Initialize the bird's rectangle
        self.bird_rect = self.bird.get_rect(center=(50, self.bird_y))

        # Buttons
        self.button_font = pygame.font.Font(None, 50)
        self.restart_button = Button(300, 250, 200, 50, "Restart", self.button_font, (100, 255, 100), (150, 255, 150), self.reset_game)
        self.quit_button = Button(300, 320, 200, 50, "Quit", self.button_font, (255, 100, 100), (255, 150, 150), self.quit_game)
        self.pause_button = Button(300, 390, 200, 50, "Pause", self.button_font, (100, 100, 255), (150, 150, 255), self.toggle_pause)

        # In-game buttons
        self.in_game_pause_button = Button(700, 10, 90, 40, "Pause", self.font, (100, 100, 255), (150, 150, 255), self.toggle_pause)
        self.in_game_quit_button = Button(700, 60, 90, 40, "Quit", self.font, (255, 100, 100), (255, 150, 150), self.quit_game)

    def create_pipe(self):
        """Creates pipes with a gap between them."""
        random_pipe_height = random.choice(self.pipe_height)

        # Adjusted pipes: Bottom pipe starts from the bottom of the screen, Top pipe is attached to the top of the screen
        top_pipe = self.pipe_surface1.get_rect(midbottom=(800, random_pipe_height))  # Top pipe connected to the top border
        bottom_pipe = self.pipe_surface2.get_rect(midtop=(800, random_pipe_height + self.pipe_gap))  # Bottom pipe resting on the bottom border
        return bottom_pipe, top_pipe

    def move_pipes(self, pipes):
        """Move pipes from right to left."""
        for pipe in pipes:
            pipe.centerx -= 5
        return [pipe for pipe in pipes if pipe.right > 0]

    def draw_pipes(self, pipes):
        """Draw the pipes on the screen."""
        for pipe in pipes:
            if pipe.bottom >= 512:  # Bottom pipe connected to the bottom
                self.screen.blit(self.pipe_surface2, pipe)
            else:  # Top pipe connected to the top
                self.screen.blit(self.pipe_surface1, pipe)

    def check_collision(self):
        """Check if the bird collides with any pipes or the ground."""
        for pipe in self.pipe_list:
            if self.bird_rect.colliderect(pipe):
                return False  # Game over

        # Check if the bird hits the ground or flies too high
        if self.bird_y >= 512 or self.bird_y < 0:
            return False

        return True

    def update_score(self):
        """Update the score when the bird successfully passes a pipe."""
        for pipe in self.pipe_list:
            if 45 < pipe.centerx < 55:  # Bird passes through a pipe's center
                self.score += 1

    def run_game(self):
        """Main game loop."""
        running = True

        while running:
            self.screen.blit(self.background, (0, 0))

            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == self.pipe_spawn_time and self.game_active and not self.paused:
                    self.pipe_list.extend(self.create_pipe())

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_active:
                    # Check buttons on Game Over screen
                    self.restart_button.handle_event(event)
                    self.quit_button.handle_event(event)
                    self.pause_button.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and self.game_active:
                    # Handle in-game button presses
                    self.in_game_pause_button.handle_event(event)
                    self.in_game_quit_button.handle_event(event)

            if self.game_active and not self.paused:
                # Get head movement
                movement_direction = self.head_controller.get_head_movement()

                # Control the bird based on head movement
                if movement_direction == 'up':
                    self.bird_movement = -5  # Move bird up
                else:
                    self.bird_movement += self.gravity  # Apply gravity

                # Update bird position
                self.bird_y += self.bird_movement
                self.bird_rect.centery = self.bird_y

                # Draw the bird
                self.screen.blit(self.bird, self.bird_rect)

                # Move and draw pipes
                self.pipe_list = self.move_pipes(self.pipe_list)
                self.draw_pipes(self.pipe_list)

                # Check collision
                self.game_active = self.check_collision()

                # Update score
                self.update_score()

                # Display score
                score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
                self.screen.blit(score_surface, (10, 10))

                # Draw in-game buttons
                self.in_game_pause_button.draw(self.screen)
                self.in_game_quit_button.draw(self.screen)

            else:
                self.display_game_over()

            # Update display
            pygame.display.update()
            self.clock.tick(30)  # 30 FPS

        self.head_controller.release()
        pygame.quit()

    def reset_game(self):
        """Reset the game variables for a new game."""
        self.bird_y = 250
        self.bird_movement = 0
        self.pipe_list.clear()
        self.score = 0
        self.bird_rect.centery = self.bird_y
        self.game_active = True
        self.paused = False

    def quit_game(self):
        """Quit the game."""
        pygame.quit()
        quit()

    def toggle_pause(self):
        """Pause or unpause the game."""
        self.paused = not self.paused

    def display_game_over(self):
        """Display the Game Over screen with buttons."""
        game_over_surface = self.font.render("Game Over!", True, (255, 0, 0))
        final_score_surface = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(game_over_surface, (300, 100))
        self.screen.blit(final_score_surface, (300, 150))

        # Draw buttons
        self.restart_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.pause_button.draw(self.screen)

# For testing purposes
if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run_game()

