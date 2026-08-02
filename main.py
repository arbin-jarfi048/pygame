import pygame
import sys
import math
import asyncio  

# 1. Initialize Pygame
pygame.init()

# Screen Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Derpy Blob's Cyber Odyssey")

# Global Colors
BG_DARK = (15, 12, 25)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Stage Themes [Platform Highlight Color, Enemy Color, Stage Name]
STAGE_THEMES = {
    1: [(0, 245, 255), (255, 0, 127), "Stage 1: Cyber Suburbs (Easy)"],
    2: [(255, 215, 0), (155, 48, 255), "Stage 2: Neon Gridlock (Medium)"],
    3: [(255, 30, 30), (57, 255, 20), "Stage 3: The Motherboard (HARD!)"]
}

# Physics Engine Constants
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.6

# 2. Player Configurations
player_w, player_h = 40, 45
player_x = 100
player_y = 400
player_vel_x = 0
player_vel_y = 0
jump_count = 0
camera_x = 0

# Game Progression Variables
current_level = 1
score = 0
game_state = "PLAYING" # PLAYING, LEVEL_CLEAR, GAME_OVER, VICTORY

# Game Assets Arrays
platforms = []
collectibles = []
enemies = []
portal_rect = pygame.Rect(2400, 430, 60, 100)

font = pygame.font.SysFont("Arial", 26, bold=True)
font_large = pygame.font.SysFont("Arial", 50, bold=True)

def load_level(level_num):
    """Generates unique maps and difficulty depending on the current stage"""
    global platforms, collectibles, enemies, player_x, player_y, player_vel_x, player_vel_y, camera_x, jump_count
    
    # Reset Player Positions
    player_x = 100
    player_y = 400
    player_vel_x = 0
    player_vel_y = 0
    camera_x = 0
    jump_count = 0
    
    # Clear out previous stage configurations
    platforms.clear()
    collectibles.clear()
    enemies.clear()
    
    if level_num == 1:
        # Stage 1 Layout: Solid ground, slow enemies
        platforms = [
            pygame.Rect(0, 530, 900, 70),
            pygame.Rect(1050, 530, 800, 70),
            pygame.Rect(1950, 530, 700, 70),
            pygame.Rect(350, 420, 150, 20),
            pygame.Rect(600, 330, 150, 20),
            pygame.Rect(1200, 410, 200, 20),
            pygame.Rect(1500, 320, 150, 20),
        ]
        enemies = [
            [pygame.Rect(450, 495, 35, 35), 2.5, 300, 800],
            [pygame.Rect(1300, 495, 35, 35), 3.0, 1100, 1600]
        ]
        
    elif level_num == 2:
        # Stage 2 Layout: Bigger Pits, Faster enemies, Floating steps
        platforms = [
            pygame.Rect(0, 530, 700, 70),
            pygame.Rect(850, 530, 600, 70),
            pygame.Rect(1600, 530, 1000, 70),
            pygame.Rect(300, 400, 120, 20),
            pygame.Rect(500, 300, 120, 20),
            pygame.Rect(750, 410, 100, 20),
            pygame.Rect(1000, 320, 120, 20),
            pygame.Rect(1300, 420, 120, 20),
            pygame.Rect(2000, 390, 150, 20),
        ]
        enemies = [
            [pygame.Rect(350, 495, 35, 35), 4.5, 100, 650],
            [pygame.Rect(950, 495, 35, 35), 5.0, 870, 1400],
            [pygame.Rect(1800, 495, 35, 35), 5.5, 1650, 2200]
        ]
        
    elif level_num == 3:
        # Stage 3 Layout: Absolute chaos. Tiny platforms, high speed hazards
        platforms = [
            pygame.Rect(0, 530, 500, 70),
            pygame.Rect(700, 530, 400, 70),
            pygame.Rect(1300, 530, 400, 70),
            pygame.Rect(1900, 530, 800, 70),
            pygame.Rect(550, 420, 80, 20),
            pygame.Rect(1150, 400, 80, 20),
            pygame.Rect(1250, 290, 80, 20),
            pygame.Rect(1750, 410, 90, 20),
            pygame.Rect(2100, 340, 100, 20),
        ]
        enemies = [
            [pygame.Rect(200, 495, 35, 35), 6.5, 50, 450],
            [pygame.Rect(800, 495, 35, 35), 7.0, 720, 1050],
            [pygame.Rect(1400, 495, 35, 35), 7.5, 1320, 1650],
            [pygame.Rect(2000, 495, 35, 35), 8.0, 1920, 2400]
        ]

    # Dynamically place collectibles floating over structural platforms
    for p in platforms[4:]:
        collectibles.append([p.x + p.width//2 - 10, p.y - 40, False])

# Initialize the first stage structure
load_level(current_level)

def draw_funny_character(x, y):
    """Draws a ridiculous squishy yellow blob with mismatched shaking googly eyes"""
    # Calculate visual squish stretching based on movement physics
    squish_x = int(player_vel_y * 0.8) if player_vel_y > 0 else int(-player_vel_y * 0.4)
    visual_w = player_w + squish_x
    visual_h = player_h - abs(squish_x)
    visual_x = x - camera_x - (squish_x // 2)
    visual_y = y + abs(squish_x)

    # Main Yellow Blob Frame
    pygame.draw.ellipse(screen, (255, 220, 40), (visual_x, visual_y, visual_w, visual_h))
    
    # Left Big Googly Eye (Stares upward/sideways)
    pygame.draw.circle(screen, WHITE, (visual_x + 12, visual_y + 14), 8)
    pygame.draw.circle(screen, BLACK, (visual_x + 10, visual_y + 10), 3)
    
    # Right Massive Googly Eye (Stares down cross-eyed)
    pygame.draw.circle(screen, WHITE, (visual_x + 28, visual_y + 16), 11)
    pygame.draw.circle(screen, BLACK, (visual_x + 28, visual_y + 20), 4)

    # Silly open smiling mouth
    pygame.draw.ellipse(screen, (150, 0, 0), (visual_x + 16, visual_y + 24, 10, 8))

    # Wobbly Dynamic Stick Legs
    time_stamp = pygame.time.get_ticks() // 60
    leg_swing = math.sin(time_stamp) * 6 if player_vel_x != 0 else 0
    
    # Left Leg & Right Leg lines
    pygame.draw.line(screen, BLACK, (visual_x + 12, visual_y + visual_h), (visual_x + 12 + leg_swing, visual_y + visual_h + 10), 3)
    pygame.draw.line(screen, BLACK, (visual_x + 26, visual_y + visual_h), (visual_x + 26 - leg_swing, visual_y + visual_h + 10), 3)

# 3. Main Operational Cycle 
async def main():
   
    global player_x, player_y, player_vel_x, player_vel_y, jump_count
    global camera_x, current_level, score, game_state
    
    running = True
    while running:
        # Key Press Interpretations
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == "PLAYING":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if jump_count < 2:
                            player_vel_y = -11.5
                            jump_count += 1
                else:
                    if event.key == pygame.K_r:
                        # Wipe variables cleanly back to Stage 1 base state
                        current_level = 1
                        score = 0
                        game_state = "PLAYING"
                        load_level(current_level)

        # Polling Active Movement Commands
        keys = pygame.key.get_pressed()
        if game_state == "PLAYING":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_vel_x = -5.5
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_vel_x = 5.5
            else:
                player_vel_x = 0

        # --- SIMULATION PHYSICS LOGIC ---
        if game_state == "PLAYING":
            # Resolve Horizontal Shifts
            player_x += player_vel_x
            player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
            for plat in platforms:
                if player_rect.colliderect(plat):
                    if player_vel_x > 0: player_x = plat.left - player_w
                    elif player_vel_x < 0: player_x = plat.right

            # Apply Acceleration Constants (Gravity updates)
            player_vel_y += GRAVITY
            player_y += player_vel_y
            
            player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
            for plat in platforms:
                if player_rect.colliderect(plat):
                    if player_vel_y > 0:
                        player_y = plat.top - player_h
                        player_vel_y = 0
                        jump_count = 0  # Re-enable double jumping capabilities
                    elif player_vel_y < 0:
                        player_y = plat.bottom
                        player_vel_y = 0

            # Boundary checks for bottomless pit deaths
            if player_y > SCREEN_HEIGHT:
                game_state = "GAME_OVER"

            # Camera scroll follow frame tracking
            if player_x - camera_x > 400:
                camera_x = player_x - 400
            elif player_x - camera_x < 150 and camera_x > 0:
                camera_x = player_x - 150

            # Process Enemy Activity Loops
            for enemy in enemies:
                enemy_rect = enemy[0]
                enemy_rect.x += enemy[1]
                if enemy_rect.x > enemy[3] or enemy_rect.x < enemy[2]:
                    enemy[1] = -enemy[1]
                
                if player_rect.colliderect(enemy_rect):
                    # Jump landing check (Stomp mechanics)
                    if player_vel_y > 0 and (player_y + player_h - player_vel_y) <= enemy_rect.top + 12:
                        player_vel_y = -8
                        enemy_rect.x = -99999 # Wipe off map field
                        score += 100
                    else:
                        game_state = "GAME_OVER"

            # Item pickup sweeps
            for col in collectibles:
                if not col[2]:
                    col_rect = pygame.Rect(col[0], col[1], 20, 20)
                    if player_rect.colliderect(col_rect):
                        col[2] = True
                        score += 25

            # Portal Gate Transitions (Checking for Next Stage Progression)
            if player_rect.colliderect(portal_rect):
                if current_level < 3:
                    current_level += 1
                    load_level(current_level)
                else:
                    game_state = "VICTORY"

        # --- RENDERING GRAPHICS ---
        screen.fill(BG_DARK)
        theme_color = STAGE_THEMES[current_level][0]
        enemy_color = STAGE_THEMES[current_level][1]

        # Draw Current Level Maps
        for plat in platforms:
            pygame.draw.rect(screen, (35, 35, 50), (plat.x - camera_x, plat.y, plat.width, plat.height), border_radius=4)
            pygame.draw.rect(screen, theme_color, (plat.x - camera_x, plat.y, plat.width, 4))

        # Render Active Level Collectibles
        for col in collectibles:
            if not col[2]:
                pygame.draw.circle(screen, theme_color, (col[0] - camera_x + 10, col[1] + 10), 9)
                pygame.draw.circle(screen, WHITE, (col[0] - camera_x + 10, col[1] + 10), 3)

        # Draw Patrolling Enemies
        for enemy in enemies:
            if enemy[0].x > -1000:
                pygame.draw.rect(screen, enemy_color, (enemy[0].x - camera_x, enemy[0].y, enemy[0].width, enemy[0].height), border_radius=8)
                # Angry glowing eyes for enemies
                pygame.draw.circle(screen, WHITE, (enemy[0].x - camera_x + 10, enemy[0].y + 12), 4)
                pygame.draw.circle(screen, WHITE, (enemy[0].x - camera_x + 25, enemy[0].y + 12), 4)

        # Render Rescue Portal Goal Post
        pygame.draw.rect(screen, (0, 255, 100), (portal_rect.x - camera_x, portal_rect.y, portal_rect.width, portal_rect.height), 3, border_radius=8)
        # The trapped buddy waiting inside the gate
        pygame.draw.circle(screen, WHITE, (portal_rect.x - camera_x + 30, portal_rect.y + 40), 10)
        pygame.draw.ellipse(screen, (240, 100, 20), (portal_rect.x - camera_x + 20, portal_rect.y + 52, 20, 25))

        # Draw the main funny character
        if game_state != "GAME_OVER":
            draw_funny_character(player_x, player_y)

        # HUD Interface Rendering Updates
        txt_stage = font.render(STAGE_THEMES[current_level][2], True, theme_color)
        txt_score = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(txt_stage, (20, 15))
        screen.blit(txt_score, (20, 45))

        # Condition Screens
        if game_state == "GAME_OVER":
            txt_lose = font_large.render("DERPY BLOB POPPED!", True, enemy_color)
            txt_retry = font.render("Press 'R' to Respawn and restart from Stage 1", True, WHITE)
            screen.blit(txt_lose, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 50))
            screen.blit(txt_retry, (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 20))
            
        elif game_state == "VICTORY":
            txt_won = font_large.render("ODYSSEY COMPLETE!", True, (0, 255, 100))
            txt_stats = font.render(f"You saved your buddy across all 3 stages! Final Score: {score}", True, WHITE)
            txt_retry = font.render("Press 'R' to play the loop again!", True, theme_color)
            screen.blit(txt_won, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 60))
            screen.blit(txt_stats, (SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 + 10))
            screen.blit(txt_retry, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)
        
        
        await asyncio.sleep(0) 

    pygame.quit()
    sys.exit()


asyncio.run(main())