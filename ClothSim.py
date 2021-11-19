import numpy as np
import pygame
from pygame.version import PygameVersion, SoftwareVersion
import pymunk
from pymunk import vec2d
from pymunk.vec2d import Vec2d

pygame.init()

display = pygame.display.set_mode((750,1000))
clock = pygame.time.Clock()
fps = 80
top, left = (300,250)
length = 20
n,m = 20,20
mass = 0.25
radius = 3
k= 1000
d = 25
g=980
sD = 0.05

class spring():
    def __init__(self) -> None:
        self.rect = pygame.Rect

def setup_space():
    space = pymunk.Space()
    space.gravity = 0,g
    space.damping = sD
    return space


def floor(space):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body,(0,900),(750,900), 5 )
    space.add(shape,body)

def add_pin(space,i):
    body = space.bodies[i]
    x,y = body.position
    pj = pymunk.PinJoint(space.static_body, body, (x, y), (0,0))
    pj.stiffness = False
    space.add(pj)

def cloth(space):
    for y in range(top-length*(n-1),top+1,length):
        for x in range(left,left+1+length*(m-1),length):
            moment = pymunk.moment_for_circle(mass, 0, radius, (0,0))
            body = pymunk.Body(mass, moment)
            body.position = x, y
            body.start_position = Vec2d(*body.position)
            shape = pymunk.Circle(body, radius)
            shape.filter = pymunk.ShapeFilter(group=1)
            space.add(body, shape)
    for i in range(len(space.shapes)):
        if i%m !=m-1:
            spring = pymunk.DampedSpring(space.bodies[i+1], space.bodies[i], (0,0), (0,0),length, k,d)
            space.add(spring)
        if i > m-1:
            spring = pymunk.DampedSpring(space.bodies[i-m], space.bodies[i], (0,0), (0,0), length, k,d)
            space.add(spring)

def cursor(space):
    moment = pymunk.moment_for_circle(mass, 0, radius, (0,0))
    body = pymunk.Body(body_type=2)
    body.position = 0,0
    body.start_position = Vec2d(*body.position)
    shape = pymunk.Circle(body, radius)
    # shape.filter = pymunk.ShapeFilter(group=1)
    shape.sensor = True
    shape.collision_type =2
    space.add(body, shape)    

def findParticle(space, x, y):
    for body in space.bodies:
        if np.linalg.norm(body.position-np.array([x,y])) <= radius:
            return body
    return None

def cutspring(space,x,y):
    for spring in space.constraints:
        a = spring.a.position
        b = spring.b.position
        c = np.array([x,y])            
        if abs(np.cross(b-a,c-a)) < 200 and 0< np.dot(b-a,c-a) < np.linalg.norm(a-b)**2:
            space.remove(spring)

def drawsprings(display,space):
    for spring in space.constraints:
        if spring.stiffness:
            a = spring.a.position
            b = spring.b.position
            pygame.draw.line(display, (255,255,255), a,b,1)

def main():
    selected_particle = None
    selected_spring = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        display.fill((0,0,0))
        for i in range(m*n):
            body = space.bodies[i]
            xr,yr = space.bodies[i-1].position
            xc,yc = space.bodies[i-m].position
            x,y = body.position
            pygame.draw.circle(display,(255,255,255),(int(x),int(y)),radius)
        drawsprings(display,space)
        pygame.draw.line(display, (255,255,255),(0,900),(750,900), 5  )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouseX, mouseY = pygame.mouse.get_pos()
            pygame.draw.circle(display,(255,255,255),(mouseX,mouseY),radius)
            selected_spring =1
            cutspring(space,mouseX,mouseY)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            selected_spring = None
        if selected_spring:
            mouseX, mouseY = pygame.mouse.get_pos()
            pygame.draw.circle(display,(255,255,255),(mouseX,mouseY),radius)
            cutspring(space,mouseX,mouseY)


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = findParticle(space, mouseX, mouseY)
    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            selected_particle = None
        if selected_particle:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle.position = ([mouseX,mouseY])
            selected_particle.velocity = ([0,0])
        pygame.display.update()
        clock.tick(fps)
        space.step(1/fps)



if __name__ == '__main__':
    space = setup_space()
    cloth(space)
    floor(space)
    for i in range(m):
        add_pin(space,i)
    # space.shapes[m*n-1].body.apply_impulse_at_local_point((25,0))
    main()