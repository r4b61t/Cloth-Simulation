import numpy as np
import pygame
import pymunk
from pymunk.vec2d import Vec2d


windowsizex, windowsizey = 750,1000
clock = pygame.time.Clock()
fps = 80
length = 20
n,m = 20,20
left,top = int((windowsizex-m*length)/2),50
mass = 0.25
radius = 3
k= 1000
d = 25
g=980
sD = 0.1

pygame.init()

display = pygame.display.set_mode((windowsizex,windowsizey))

def setup_space():
    space = pymunk.Space()
    space.gravity = 0,g
    space.damping = sD
    return space


def floor(space):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body,(0,windowsizey -100),(windowsizex,windowsizey-100), 5 )
    space.add(shape,body)

def add_pin(space,i):
    body = space.bodies[i]
    x,y = body.position
    pin = pymunk.PinJoint(space.static_body, body, (x, y), (0,0))
    pin.stiffness = False
    pin.id = 3
    space.add(pin)

def cloth(space):
    for y in range(top,top+length*(n),length):
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
            spring.id =0
            space.add(spring)
        if i > m-1:
            spring = pymunk.DampedSpring(space.bodies[i-m], space.bodies[i], (0,0), (0,0), length, k,d)
            spring.id =0
            space.add(spring)

def cursor(space):
    body = pymunk.Body(body_type=2)
    body.position = 0,0
    body.start_position = Vec2d(*body.position)
    shape = pymunk.Circle(body, radius)
    shape.sensor = True
    space.add(body, shape)    

def findParticle(space, x, y):
    for body in space.bodies:
        if Vec2d.get_distance(body.position,Vec2d(x,y)) <= length:
            return body
    return None

def cutspring(space,x,y):
    for spring in space.constraints:
        a = spring.a.position
        b = spring.b.position
        c = np.array([x,y])            
        if abs((b-a).cross(c-a)) < 200 and 0< (b-a).dot(c-a) < (a-b).get_length_sqrd() and spring.id == 0:
            space.remove(spring)

def drawsprings(display,space):
    for spring in space.constraints:
        if spring.id == 0:
            a = spring.a.position
            b = spring.b.position
            pygame.draw.line(display, (255,255,255), a,b,1)

def drawparticles(display,space):
    for body in space.bodies:
        if body.body_type != 2:
            x,y = body.position
            pygame.draw.circle(display,(255,255,255),(int(x),int(y)),radius)

def addcursor(space,particle):
    cursor(space)
    spring = pymunk.DampedSpring(particle, space.bodies[-1], (0,0), (0,0), 0, k,d)
    spring.id = 1
    space.add(spring)

def removecursor(space):
    for body in space.bodies:
        if body.body_type == 2:
            space.remove(body)
    for spring in space.constraints:
        if spring.id == 1:
            space.remove(spring)

def main():
    selected_particle = None
    selected_spring = None
    cursor = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        display.fill((0,0,0))

        drawparticles(display,space)
        drawsprings(display,space)

        pygame.draw.line(display, (255,255,255),(0,900),(windowsizex,900), 5  )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            (mouseX, mouseY) = pygame.mouse.get_pos()
            pygame.draw.circle(display,(0,0,255),(mouseX,mouseY),radius)
            selected_particle = findParticle(space, mouseX, mouseY)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            removecursor(space)
            cursor = None
            selected_particle = None
        if selected_particle:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            pygame.draw.circle(display,(0,0,255),(mouseX,mouseY),radius)
            if cursor == None:
                addcursor(space,selected_particle)
                cursor = space.bodies[-1]
            space.bodies[-1].position = ([mouseX,mouseY])
            space.bodies[-1].velocity = ([0,0])
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouseX, mouseY = pygame.mouse.get_pos()
            pygame.draw.circle(display,(255,0,0),(mouseX,mouseY),radius)
            selected_spring =1
            cutspring(space,mouseX,mouseY)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            selected_spring = None
        if selected_spring:
            mouseX, mouseY = pygame.mouse.get_pos()
            pygame.draw.circle(display,(255,0,0),(mouseX,mouseY),radius)
            cutspring(space,mouseX,mouseY)

        pygame.display.update()
        clock.tick(fps)
        space.step(1/fps)



if __name__ == '__main__':
    space = setup_space()
    cloth(space)
    floor(space)
    for i in range(m):
        add_pin(space,i)
    main()