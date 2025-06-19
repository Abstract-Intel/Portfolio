import pygame
import random
import math

# Config
WIDTH, HEIGHT = 800, 600
NUM_PARTICLES = 400
PARTICLE_TYPES = ['A', 'B', 'C', 'D', 'E']
TYPE_COLORS = {
    'A': (255, 100, 100),  # Core attractor - red
    'B': (100, 255, 100),  # Membrane - green
    'C': (100, 100, 255),  # Passive filler - blue
    'D': (255, 255, 100),  # Neutral background - yellow
    'E': (200, 100, 255)   # Chaotic disruptor - purple
}

# Interaction rules for membrane formation (cleaned & meaningful)
INTERACTION_RULES = {
    # A (Core): Strong cohesion and attraction with D (to draw a soft shell)
    ('A', 'A'):  0.8,
    ('A', 'B'):  0.3,
    ('A', 'C'):  0.1,
    ('A', 'D'):  0.5,
    ('A', 'E'): -0.4,

    # B (Membrane): Slight attraction to A and self, mild cohesion
    ('B', 'A'):  0.3,
    ('B', 'B'):  0.2,
    ('B', 'C'):  0.2,
    ('B', 'D'):  0.0,
    ('B', 'E'): -0.3,

    # C (Passive): Neutral or weakly attractive
    ('C', 'A'):  0.1,
    ('C', 'B'):  0.2,
    ('C', 'C'):  0.0,
    ('C', 'D'):  0.0,
    ('C', 'E'): -0.1,

    # D (Outer Shell / Overflow): Repelled by core
    ('D', 'A'): -0.5,
    ('D', 'B'):  0.0,
    ('D', 'C'):  0.0,
    ('D', 'D'):  0.0,
    ('D', 'E'):  0.0,

    # E (Disruptor): Repels core and membrane, causes chaos
    ('E', 'A'): -0.4,
    ('E', 'B'): -0.3,
    ('E', 'C'): -0.1,
    ('E', 'D'):  0.0,
    ('E', 'E'):  0.0,
}


MUTATION_CHANCE = 0.1          # Chance to mutate on replication
REPLICATION_RADIUS = 12        # Radius to detect cluster for replication
REPLICATION_COOLDOWN = 10
MAX_FORCE = 0.6
RADIUS = 100
PARTICLE_RADIUS = 3
MAX_AGE = 1000                 # Particle lifespan
MAX_PARTICLES = 1000           # Max number of particles allowed

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def weighted_choice():
    # Weight initial particle types: more A and C for core and filler dominance
    return random.choices(['A', 'B', 'C', 'D', 'E'], weights=[10, 3, 5, 2, 1])[0]

class Particle:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.ptype = ptype
        self.age = 0
        self.replication_timer = 0

    def update(self, particles):
        fx, fy = 0, 0
        for p in particles:
            if p is self:
                continue
            dx = p.x - self.x
            dy = p.y - self.y
            dist = math.hypot(dx, dy)
            if 1 < dist < RADIUS:
                strength = INTERACTION_RULES.get((self.ptype, p.ptype), 0)
                fx += strength * dx / dist
                fy += strength * dy / dist

        # Apply force with max limit
        self.vx += max(-MAX_FORCE, min(fx, MAX_FORCE))
        self.vy += max(-MAX_FORCE, min(fy, MAX_FORCE))

        # Limit speed
        speed = math.hypot(self.vx, self.vy)
        if speed > 2:
            self.vx *= 2 / speed
            self.vy *= 2 / speed

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep particle inside screen bounds with bounce
        if self.x < PARTICLE_RADIUS:
            self.x = PARTICLE_RADIUS
            self.vx *= -0.5
        elif self.x > WIDTH - PARTICLE_RADIUS:
            self.x = WIDTH - PARTICLE_RADIUS
            self.vx *= -0.5

        if self.y < PARTICLE_RADIUS:
            self.y = PARTICLE_RADIUS
            self.vy *= -0.5
        elif self.y > HEIGHT - PARTICLE_RADIUS:
            self.y = HEIGHT - PARTICLE_RADIUS
            self.vy *= -0.5

        self.age += 1
        self.replication_timer += 1

        # Remove particle if too old
        if self.age > MAX_AGE:
            particles.remove(self)
            return

        # Try replication after cooldown
        if self.replication_timer > REPLICATION_COOLDOWN:
            self.try_replicate(particles)

    def try_replicate(self, particles):
        nearby = [p for p in particles if p is not self and math.hypot(p.x - self.x, p.y - self.y) < REPLICATION_RADIUS and p.ptype == self.ptype]
        if len(nearby) > 1 and len(particles) < MAX_PARTICLES:
            new_type = self.ptype
            if random.random() < MUTATION_CHANCE:
                new_type = random.choice(PARTICLE_TYPES)
            particles.append(Particle(
                (self.x + random.uniform(-2, 2)),
                (self.y + random.uniform(-2, 2)),
                new_type
            ))
            self.replication_timer = 0

    def draw(self, surface):
        color = TYPE_COLORS[self.ptype]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), PARTICLE_RADIUS)

# Initialize particles
particles = [Particle(
    random.randint(PARTICLE_RADIUS, WIDTH - PARTICLE_RADIUS),
    random.randint(PARTICLE_RADIUS, HEIGHT - PARTICLE_RADIUS),
    weighted_choice()
) for _ in range(NUM_PARTICLES)]

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw all particles
    for p in particles[:]:  # Copy list since we may remove particles
        p.update(particles)
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
