from dataclasses import dataclass

import numpy as np
import pygame
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SPACING = 10.
n,m = 7,40
k = 50
density = 1
mass = density * n *m
D= 50
g = 1
pinned = True
@dataclass
class Particle:
    position: np.array
    velocity: np.array
    radius: float = 5

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, center=self.position, radius=self.radius)

    def update(self, acceleration: np.array, dt=1.0):
        self.position = self.position + self.velocity * dt + 0.5 * acceleration * dt ** 2
        self.velocity = self.velocity + acceleration * dt

    def move_to(self, x, y):
        self.position = np.array(x, y)
@dataclass
class spring:
    start_pos: np.array
    end_pos: np.array 
    width: 0.5

    def draw(self,surf):
        pygame.draw.line(surf,WHITE,start_pos= self.start_pos,end_pos = self.end_pos)

def setup_pygame():
    pygame.init() 
    w, h = (2000, 1000)
    screen = pygame.display.set_mode((w, h))
    surf = pygame.Surface((w, h))
    #text display 
    font = pygame.font.SysFont("comicsansms", 12)
    texts = [font.render(f'mass = {mass} ',True,(WHITE)),
    font.render(f'damp = {D}',True,(WHITE)),
    font.render(f'g = {g}',True,(WHITE)),
    font.render(f'k = {k}',True,(WHITE)),
    font.render(f'top row pin = {pinned}',True,(WHITE))
    ]
    pygame.display.set_caption('softbody physics')
    return screen, surf ,texts


def unit_vector(v: np.array) -> np.array:
    return v / np.linalg.norm(v)
def gravity(a:Particle):
    return np.array([0.,1])*g*mass
def damp(D,p):
    return -D*p.velocity
def wind(a:Particle):
    return np.array([1.,0])*w
def force_on(a: Particle, source: Particle) -> np.array:
    a2s = source.position - a.position
    f = (np.linalg.norm(a2s) - SPACING) * k * unit_vector(a2s)
    return f
def spring_pe(a: Particle, source: Particle):
    a2s = source.position - a.position
    f = (np.linalg.norm(a2s) - SPACING)**2*0.5 * k
    return f
def calculate_forces(particles: np.array):
    n_row, n_col = particles.shape
    forces = np.zeros((n_row, n_col), dtype=object)
    for i_row, p_row in enumerate(particles):
        for i_col, p in enumerate(p_row):
            total_force = np.array([0., 0.])
            if i_row > 0:  # top
                total_force += force_on(p, particles[i_row - 1, i_col]) +gravity(particles) + damp(D,p) 
            if i_row < n_row - 1:  # bottom
                total_force += force_on(p, particles[i_row + 1, i_col]) + damp(D,p) 
            if i_col > 0:  # left
                total_force += force_on(p, particles[i_row, i_col - 1])+ damp(D,p)  
            if i_col < n_col - 1:  # right
                total_force += force_on(p, particles[i_row, i_col + 1])+ damp(D,p) 
            forces[i_row, i_col] = total_force
    return forces
def total_KE(particles:np.array):
    energy = 0
    for i_row, p_row in enumerate(particles):
        for i_col, p in enumerate(p_row):
            energy +=  0.5*mass*np.linalg.norm(p.velocity)
    return energy
def total_PE(particles:np.array):
    energy = 0
    n_row, n_col = particles.shape
    for i_row, p_row in enumerate(particles):
        for i_col, p in enumerate(p_row):
            if i_row > 0:  # top
                energy += spring_pe(p, particles[i_row - 1, i_col]) 
            if i_row < n_row - 1:  # bottom
                energy += spring_pe(p, particles[i_row + 1, i_col]) 
            if i_col > 0:  # left
                energy += spring_pe(p, particles[i_row, i_col - 1])
            if i_col < n_col - 1:  # right
                energy += spring_pe(p, particles[i_row, i_col + 1])
    return energy
def draw_spring(particles,surf):
    n_row, n_col = particles.shape
    for i_row, p_row in enumerate(particles):
        for i_col, p in enumerate(p_row):
            if i_row > 0:  # top
                spring(start_pos = p.position, end_pos = particles[i_row - 1, i_col].position,width=0.5).draw(surf)
            if i_col > 0:  # left
                spring(start_pos = p.position, end_pos =particles[i_row, i_col - 1].position,width=0.5).draw(surf)

def findParticle(particles, x, y):
    for i in particles:
        for p in i:
            if np.linalg.norm(p.position-np.array([x,y])) <= p.radius:
                return p
    return None

def check_position(particles):
    for i in particles:
        for p in i :
            print(p.position)            
    pass

def main():
    running = True

    screen, surf ,texts = setup_pygame()
    
    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()
    i_frame = 0
    n_row, n_col = n,m
    particles = np.array([[Particle(position=np.array([(i_col + 1) * SPACING+50, 50+(i_row + 1) * SPACING]),
                                    velocity=np.array([0, 0]))
                           for i_col in range(n_col)] for i_row in range(n_row)])
    check_position(particles)
    selected_particle = None
    while running:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                running = False  # Flag that we are done so we exit this loop

        if event.type == pygame.MOUSEBUTTONDOWN:            
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = findParticle(particles, mouseX, mouseY)

        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None
        if selected_particle:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle.position = np.array([mouseX,mouseY])
            selected_particle.velocity = np.array([0,0])
        surf.fill(BLACK)

        forces = calculate_forces(particles)
        for i_row, p_row in enumerate(particles):
            for i_col, p in enumerate(p_row):
                if i_row !=0 or  not pinned:
                    p.update(forces[i_row, i_col]/mass)
                p.draw(surf)
        draw_spring(particles,surf)
        screen.blit(surf, (0, 0))
        for i in range(len(texts)):
            screen.blit(texts[i],(1850,20+15*i))
        pygame.display.flip()
        clock.tick(60)
        i_frame += 1
    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()


if __name__ == '__main__':
    main()
