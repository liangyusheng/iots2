import time
import random
import displayio
import adafruit_imageload
from hiibot_iots2 import IoTs2
iots2 = IoTs2()
screen = iots2.screen
screen.rotation = 270  # button on the left-hand
group = displayio.Group()

############# load some bitmaps to layout our game screen ############

# Load ground bitmap
ground_bmp, palette = adafruit_imageload.load("/imgs/ground512x12.bmp",
                                              bitmap=displayio.Bitmap,
                                              palette=displayio.Palette)
palette.make_transparent(1)
palette[0] = 0x808000
ground = displayio.TileGrid(ground_bmp, pixel_shader=palette,
                            width=120, height=1,
                            tile_width=2, tile_height=12,
                            x=0, y=120)
for x in range(120):
    ground[x] = x
group.append(ground)

# Load dinosaur bitmap
dinosaur_bmp, palette = adafruit_imageload.load("/imgs/dinosaur132x47.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
palette.make_transparent(1)
palette[0] = 0x404040
dinosaur = displayio.TileGrid(dinosaur_bmp, pixel_shader=palette,
                              width=1, height=1,
                              tile_width=44, tile_height=47, 
                              default_tile=2)
dinosaur.x = 8
dinosaur.y = 90
group.append(dinosaur)

# Load small cactus bitmap
cactus1_bmp, palette = adafruit_imageload.load("/imgs/cactus15x32.bmp",
                                              bitmap=displayio.Bitmap,
                                              palette=displayio.Palette)
palette.make_transparent(1)
palette[0] = 0x008000
cactus1 = displayio.TileGrid(cactus1_bmp, pixel_shader=palette)
cactus1.x = 240
cactus1.y = 94
group.append(cactus1)

# Load large cactus bitmap
cactus2_bmp, palette = adafruit_imageload.load("/imgs/cactus24x50.bmp",
                                               bitmap=displayio.Bitmap,
                                               palette=displayio.Palette)
palette.make_transparent(1)
palette[0] = 0x008000
cactus2 = displayio.TileGrid(cactus2_bmp, pixel_shader=palette)
cactus2.flip_x = True
cactus2.y = 76
group.append(cactus2)

# Load digital (score) bitmap
digital_bmp, palette = adafruit_imageload.load("/imgs/digital200x25.bmp",
                                               bitmap=displayio.Bitmap,
                                               palette=displayio.Palette)
palette.make_transparent(1)
palette[0] = 0x220022
score = displayio.TileGrid(digital_bmp, pixel_shader=palette,
                           width=3, height=1,
                           tile_width=20, tile_height=25)
score.x = 176
score.y = 4
group.append(score)

def update_score(points):
    score[2] = points % 10
    score[1] = (points // 10) % 10
    score[0] = (points // 100) % 10

# Load game_over bitmap
game_over_bmp, palette2 = adafruit_imageload.load("/imgs/game_over190x10.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)
palette2.make_transparent(1)
palette2[0] = 0xFF0000
game_over = displayio.TileGrid(game_over_bmp, pixel_shader=palette2)
game_over.x = 240
game_over.y = 66
game_over.hidden = True
group.append(game_over)

# Load cloud bitmap
cloud_bmp, palette2 = adafruit_imageload.load("/imgs/cloud92x27.bmp",
                                              bitmap=displayio.Bitmap,
                                              palette=displayio.Palette)
palette2.make_transparent(15)
cloud = displayio.TileGrid(cloud_bmp, pixel_shader=palette2)
cloud.x = 80
cloud.y = 20
group.append(cloud)

######################## ready to run our game ######################

ledToogle = False
iots2.blueLED_bright = 0.0
screen.show(group)
demo = True # demo mode is default, auto-running!

deltaY = [-32, -16, -8, -6, -5, -4, -3, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 16, 32]

while True :
    t = 0
    jump = -1
    points = 0
    update_score(0)

    dinosaur.y = 82  # (8, 160)
    cactus1.x = 240  # (240, 170)
    cactus2.x = 480  # (480, 154)

    while True :
        # move the ground with fastest speed
        for x in range(120):
            ground[x] = (t+x) & 0xFF
        # move the small cactus (change its x coordinate)
        cactus1.x -= 2
        if cactus1.x<-15 :
            cactus1.x = cactus2.x + 120 + 2*random.randint(0, 255)
            #print((cactus1.x, cactus2.x))
        # move the large cactus (change its x coordinate)
        cactus2.x -= 2
        if cactus2.x<-24 :
            cactus2.x = cactus1.x + 120 + 2*random.randint(0, 255)
            #print((cactus1.x, cactus2.x))
        # move cloud ( change the x coordinate of cloud)
        if (t&7)==0 :
            cloud.x -= 1
            if cloud.x < -92 :
                cloud.x = 240 + random.randint(0, 15)
        
        # Button be pressed, then quit out demo mode, and ready to jump
        if jump<0 and iots2.button_state :
            jump = 0
            dinosaur[0, 0] = 2
            if demo :
                demo = False
                points = 0
                update_score(0)
                palette[0] = 0xCC0022
                dinosaur.pixel_shader = palette
        # ready to jump in demo mode
        if demo and jump<0 and (cactus1.x==52 or cactus2.x==52) :
            jump = 0
            dinosaur[0, 0] = 2
        # jump or not
        if jump>=0 :
            dinosaur.y += deltaY[jump]
            jump += 1
            if jump>=len(deltaY) :
                jump = -1
        else :
            if (t&7)==0 :
                dinosaur[0, 0] = (t >> 3) & 1

        # add score
        if cactus1.x==0 or cactus2.x==0 :
            points += 1
            update_score(points)
        # refresh the screen to generate animation effects
        screen.show(group)
        
        # game over
        if (8<cactus1.x and cactus1.x<36 and (dinosaur.y+44)>=cactus1.y) or (8<cactus2.x and cactus2.x<36 and (dinosaur.y+44)>=(cactus2.y)) :
            print((cactus1.x, cactus2.x, dinosaur.y))
            game_over.hidden = False
            game_over.x = 25
            screen.show(group)
            iots2.blueLED_bright = 0.5
            time.sleep(1)
            while not iots2.button_state : # wait for Button pressed to restart
                time.sleep(0.1)

            time.sleep(1)
            while iots2.button_state : # wait for Button released
                time.sleep(0.1)
            game_over.x = 240
            game_over.hidden = True
            print('restart')
            iots2.blueLED_bright = 0.0
            break
        # change t with 1
        t = (t+1) & 0xFF
        time.sleep(0.002)
