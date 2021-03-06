from win32api import GetSystemMetrics
from fun import *
from image_process import get_data
import random
import sys
import cv2
from menu import *
import imutils

# create thumbnail
levels_dir = os.listdir('images/levels')
for i in range(len(levels_dir)):
    name = 'images/levels/' + levels_dir[i]
    filename = "%s" % name

    img = cv2.imread(filename)
    hor_size = img.shape[1]
    ver_size = img.shape[0]

    # rotate & resize
    if ver_size > hor_size:
        img = imutils.rotate_bound(img, -90)
    hor_size = img.shape[1]
    ver_size = img.shape[0]
    max_dim = max(hor_size, ver_size)
    rule = 200
    r = rule / img.shape[1]
    dim = (int(rule), int(img.shape[0] * r))
    if max_dim > rule:
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    new_name = 'images/thumbnail/' + levels_dir[i]
    filename = "%s" % new_name
    cv2.imwrite(filename, img)
    counter = 0


def main(counter):
    screen = screen_size(1920, 1080, True)
    set_background_image("images/bg_max.jpg")
    screen_size_x = GetSystemMetrics(0)
    screen_size_y = GetSystemMetrics(1)

    counter = start_menu(counter)

    levels_dir = os.listdir('images/levels')
    name = 'images/levels/' + levels_dir[counter]
    filename = "%s" % name

    edge, new_img, list_obj = get_data(filename)
    cv2.imwrite("images/detection_output.jpg", new_img)
    aster_list = []
    worm_list = []

    for i in range(len(list_obj)):
        area = list_obj[i].area
        if len(list_obj[i].coor) < 4:
            if area > 2000:
                file = "images/planet3_100_1.png"
            elif area > 1000:
                file = "images/planet1_75_1.png"
            else:
                file = "images/aster_50_1.png"

            stripe = make_sprite("images/stripe_1080_1_dashed.png")
            stripe.move(list_obj[i].center[0], screen_size_y / 2, True)

            sprite = make_sprite(file)
            sprite.move(list_obj[i].center[0], list_obj[i].center[1], True)
            sprite.x = list_obj[i].center[0]
            sprite.y = list_obj[i].center[1]
            sprite.xspeed = 0
            sprite.yspeed = (area / 300) * ((-1) ** random.randrange(0, 100))
            sprite.changeImage(0)
            aster_list.append(sprite)
            show_sprite(sprite)
        else:
            sprite = make_sprite("images/wormhole_50_1.png")
            sprite.move(list_obj[i].center[0], list_obj[i].center[1], True)
            sprite.changeImage(0)
            worm_list.append(sprite)
            show_sprite(sprite)

    mars = make_sprite("images/mars_100_1.png")
    mars.move(screen_size_x, screen_size_y / 2, True)
    show_sprite(mars)

    # CAR parameters
    car = make_sprite("images/tesla_small0_1.png")
    add_sprite_image(car, "images/tesla_small1_1.png")
    add_sprite_image(car, "images/tesla_small2_1.png")

    car.health = 3
    car.thrustAmount = 0.7

    car.xPos = 20
    car.yPos = screen_size_y / 2
    car.xSpeed = 0
    car.ySpeed = 0
    car.slow_down = 0.05
    car.slow_down_auto = 0.001
    car.speed_lim = 40

    car.angle = 0
    car.angle_speed = 0
    car.angle_change = 0.3
    car.angle_speed_slow_down = 0.05
    car.angle_speed_slow_down_auto = 0.05
    car.angle_speed_lim = 20

    move_sprite(car, car.xPos, car.yPos, True)
    show_sprite(car)

    # labels
    life = make_label("Life:", 30, 10, 10, "white")
    change_label(life, "Life: {0}".format(str(car.health)))
    show_label(life)
    thrust_frame = 1
    nextframe = clock()

    calc_fuel = (len(aster_list)) * 3
    if len(aster_list) == 0 or calc_fuel < 20:
        calc_fuel = 20

    car.fuel = calc_fuel
    fuel_dis = make_label("Fuel:", 30, 10, 40, "white")
    change_label(fuel_dis, "Fuel: {0}".format(str(car.fuel)))
    show_label(fuel_dis)

    fps_display = make_label("FPS:", 30, 10, 70, "white")
    show_label(fps_display)

    time_pass = clock()

    first_time_nofuel = 0
    first_time_wormhole = 0

    while 1:

        if car.fuel <= 0:
            if first_time_nofuel == 0:
                time_pass = clock() + 3000
                first_time_nofuel += 1
            else:
                if car.health > 1:
                    if time_pass < clock():
                        restart(car)
                        first_time_nofuel = 0
                        first_time_wormhole = 0
                else:
                    if time_pass < clock():
                        restart_game(counter)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            temp = counter
            counter = start_menu(counter)
            if temp != counter:
                restart_game(counter)

        if key_press("r"):
            car.xSpeed = 0
            car.ySpeed = 0
            car.xPos = 50
            car.yPos = screen_size_y / 2
            car.angle_speed = 0
            car.angle = 0
            transform_sprite(car, car.angle, 1)

        if key_press("left"):
            car.angle_speed -= car.angle_change
        elif key_press("right"):
            car.angle_speed += car.angle_change

        if key_press("up"):
            if car.fuel > 0:
                car.fuel -= 1
                change_label(fuel_dis, "Fuel: {0}".format(str(car.fuel)))
                if clock() > nextframe:
                    nextframe = clock() + 50
                    if thrust_frame == 1:
                        change_sprite_image(car, 1)
                        thrust_frame = 2
                    else:
                        change_sprite_image(car, 2)
                        thrust_frame = 1
            else:
                change_sprite_image(car, 0)

            if car.fuel > 0:
                car.xSpeed += math.sin(math.radians(car.angle)) * car.thrustAmount
                car.ySpeed -= math.cos(math.radians(car.angle)) * car.thrustAmount

            if car.angle_speed != 0:
                if car.angle_speed >= 0:
                    car.angle_speed -= car.angle_speed_slow_down
                else:
                    car.angle_speed += car.angle_speed_slow_down
        elif key_press("down"):
            # slow down
            change_sprite_image(car, 0)
            if car.xSpeed > 0:
                car.xSpeed -= car.slow_down * abs(car.xSpeed)
            elif car.xSpeed <= 0:
                car.xSpeed += car.slow_down * abs(car.xSpeed)
            if car.ySpeed > 0:
                car.ySpeed -= car.slow_down * abs(car.ySpeed)
            elif car.ySpeed <= 0:
                car.ySpeed += car.slow_down * abs(car.ySpeed)
            # angle speed slow down
            if car.angle_speed != 0:
                if car.angle_speed >= 0:
                    car.angle_speed -= car.angle_speed_slow_down * abs(car.angle_speed)
                else:
                    car.angle_speed += car.angle_speed_slow_down * abs(car.angle_speed)
        elif not (key_press("left") or key_press("right")):
            # slow down auto
            change_sprite_image(car, 0)
            if car.xSpeed > 0:
                car.xSpeed -= car.slow_down_auto * abs(car.xSpeed)
            elif car.xSpeed <= 0:
                car.xSpeed += car.slow_down_auto * abs(car.xSpeed)
            if car.ySpeed > 0:
                car.ySpeed -= car.slow_down_auto * abs(car.ySpeed)
            elif car.ySpeed <= 0:
                car.ySpeed += car.slow_down_auto * abs(car.ySpeed)
            # angle speed slow down auto
            if car.angle_speed > 0:
                car.angle_speed -= car.angle_speed_slow_down_auto * abs(car.angle_speed)
            else:
                car.angle_speed += car.angle_speed_slow_down_auto * abs(car.angle_speed)

        hide = 20
        # car speed limit
        if car.xSpeed > car.speed_lim:
            car.xSpeed = car.speed_lim
        elif car.xSpeed < -car.speed_lim:
            car.xSpeed = -car.speed_lim
        if car.ySpeed > car.speed_lim:
            car.ySpeed = car.speed_lim
        elif car.ySpeed < -car.speed_lim:
            car.ySpeed = -car.speed_lim

        # update position and bounce
        car.xPos += car.xSpeed
        if car.xPos > screen_size_x + hide:
            if car.health > 1:
                # bounce_ver(car)
                restart(car)
            else:
                # bounce_ver(car)
                restart_game(counter)
        elif car.xPos < -hide:
            bounce_ver(car)
        car.yPos += car.ySpeed
        if car.yPos > screen_size_y + hide:
            bounce_hor(car)
        elif car.yPos < -hide:
            bounce_hor(car)
        move_sprite(car, car.xPos, car.yPos, True)

        # update angle & angle speed limit
        if car.angle_speed > car.angle_speed_lim:
            car.angle_speed = car.angle_speed_lim
        elif car.angle_speed < -car.angle_speed_lim:
            car.angle_speed = -car.angle_speed_lim
        car.angle += car.angle_speed
        transform_sprite(car, car.angle, 1)

        # update asteroid position
        for i in aster_list:
            hide = int(i.originalWidth)
            i.x += i.xspeed
            if i.x > screen_size_x + hide:
                i.x = -hide
            elif i.x < -hide:
                i.x = screen_size_x + hide
            i.y += i.yspeed
            if i.y > screen_size_y + hide:
                i.y = -hide
            elif i.y < -hide:
                i.y = screen_size_y + hide
            move_sprite(i, i.x, i.y, True)

        def restart_game(counter):
            hide_all()
            hide_label(fps_display)
            hide_label(fuel_dis)
            hide_label(life)
            main(counter)

        def restart(car):
            car.health -= 1
            change_label(life, "Life: {0}".format(str(car.health)))
            car.xSpeed = 0
            car.ySpeed = 0
            car.xPos = 50
            car.yPos = screen_size_y / 2
            car.angle_speed = 0
            car.fuel = calc_fuel
            change_label(fuel_dis, "Fuel: {0}".format(str(car.fuel)))
            transform_sprite(car, car.angle, 1)

        def bounce_ver(car):
            car.xSpeed = (-1) * car.xSpeed

        def bounce_hor(car):
            car.ySpeed = (-1) * car.ySpeed

        hit = all_colliding(car)
        # wormhole algorithm
        if len(hit) > 0:
            if hit[-1] in worm_list:
                if first_time_wormhole == 0:
                    rand = len(worm_list) - 1
                if hit[-1] != worm_list[rand]:
                    index = worm_list.index(hit[-1])
                    rand = random.randrange(0, len(worm_list))
                    while rand == index:
                        rand = random.randrange(0, len(worm_list))
                    car.xPos, car.yPos = worm_list[rand].rect.center
                    first_time_wormhole += 1
            elif hit[-1] in aster_list:
                if car.health > 1:
                    restart(car)
                    first_time_wormhole = 0
                else:
                    restart_game(counter)
            else:
                restart_game(counter)

        fps = tick(60)
        change_label(fps_display, "FPS: {0}".format(str(round(fps))))
        # change_label(fps_display, "FPS: {0}".format(str(round(fps, 2))))


main(counter)
