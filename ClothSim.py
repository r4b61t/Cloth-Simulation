import pygame
import pymunk
from pymunk.vec2d import Vec2d


windowsizex, windowsizey = 1200,1000
clock = pygame.time.Clock()
fps = 80
length = 10
n,m = 40,40
left,top = int((windowsizex-m*length)/2),50
mass = 0.25
radius = 1
k= 1000
d = 25
g=980
air = 0.25

pygame.init()

display = pygame.display.set_mode((windowsizex,windowsizey))

def setup_space():
    space = pymunk.Space()
    space.gravity = 0,g
    space.damping = air
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

def findParticle(space, c):
    for body in space.bodies:
        if Vec2d.get_distance(body.position,c) <= length*2:
            return body
    return None

def cutspring(space,c):
    for spring in space.constraints:
        a = spring.a.position
        if (-10 < a[0] - c[0] < 10 or -10 < a[1] - c[1] < 10) and  spring.id ==0 :
            b = spring.b.position           
            if -200 < (b-a).cross(c-a) < 200 and 0< (c-a).dot(b-a) < (b-a).get_length_sqrd() :
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

        pygame.draw.line(display, (255,255,255),(0,900),(windowsizex,900), 10  )
        c = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            pygame.draw.circle(display,(0,0,255),c,radius)
            selected_particle = findParticle(space, c)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            removecursor(space)
            cursor = None
            selected_particle = None
        if selected_particle:
            pygame.draw.circle(display,(0,0,255),c,radius)
            if cursor == None:
                addcursor(space,selected_particle)
                cursor = space.bodies[-1]
            space.bodies[-1].position = (c)
            space.bodies[-1].velocity = ([0,0])


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pygame.draw.circle(display,(255,0,0),c,radius)
            selected_spring =1
            cutspring(space,c)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            selected_spring = None
        if selected_spring:
            pygame.draw.circle(display,(255,0,0),c,radius)
            cutspring(space,c)
        
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