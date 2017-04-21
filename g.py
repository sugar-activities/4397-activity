# g.py - globals
import pygame,utils,random

app='Castle'; ver='1.0'
ver='2.0'
# sugar coated
ver='2.1'
# increased hot area in player_in() to work on XO
ver='2.2'
ver='2.3'
# check_connects takes into account direction of movement
# resized laser map
# improved map facility
# top up room 15 with diamonds
# pale shield in Laser Cave
# trapdoor location more variable
# added start to best display
ver='2.4'
# ice rink more slippery
ver='3.0'
# includes arrow keys
ver='3.1'
# removed room name
# list.index() method not used (not in Python 2.5) -> cas value(jewel)
# filled in ladder
ver='3.2'
# trap changes between visits
ver='3.3'
# teleporter - don't show XO when teleporting
#            - space = put down as well as any click
#            - doesn't visit teleporter when teleporting

def init(): # called by run()
    random.seed()
    global redraw
    global screen,w,h,pointer,font1,font2,font3,clock
    global factor,offset,imgf,message,version_display,frame_rate
    redraw=True
    version_display=False; frame_rate=0
    screen = pygame.display.get_surface()
    screen.fill((80,0,80)); pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(app)
    clock=pygame.time.Clock()
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    if pygame.font:
        t=int(50*imgf); font1=pygame.font.Font(None,t)
        t=int(100*imgf); font2=pygame.font.Font(None,t)
        t=int(108*imgf); font3=pygame.font.Font(None,t)
    pointer=utils.load_image('pointer.png',True)
    message=''
    (mx,my)=pygame.mouse.get_pos() # used by utils.mouse_on_img()
    
    # this activity only
    global bgd_colour,maxw,maxh
    global x0,y0,s0,x1,y1,best,ww,ow,cx,cy
    global player,player_pale
    global player_cx,player_cy,player_ms,player_k
    global player_w,player_h
    global direction,yn,ys,xe,xw
    global bag,bag_img,bag_glow,bag_full,bag_x,bag_y,bag_current_img
    global bag_cxy,bag_ms,bag_full_ms
    global door,open_door,window,window_ladder
    global room_ms,room_delay
    global wishes,wish_img,wish_glow,wish_current_img,wish_cxy,wish_ms
    global wish_x,wish_y
    global objects,floor
    global box_open,box_closed,box_x,box_o_y,box_c_y,score,score_c
    global box_cxy,box_glow,box_current_img,box_ms
    global green_hole,hole,trap_x,trap_y,trap_ms,state
    global inside_bag_cxy,inside_bag,clouds,bag_base
    global casino_running,casino_count,casino_delay,casino_ms,casino_obj,\
           casino_cxy
    global token,fuel
    global health,health_c,health_imgs,laser_ms,gas_ms
    global steal,steal_xy,take_ms,steal_ms,take_delay
    global telep_ms,map1_grid,map1,map1_d,map1_xy,map2,map2_rect,wishes3
    global laser_map,star
    bgd_colour=(80,0,80); maxw=0; maxh=0
    n=17
    x0=sx(1.5); y0=sy(1.5); s0=sy(n) # room display
    yn=y0; ys=y0+s0; xw=x0; xe=x0+s0; cx=x0+s0/2; cy=y0+s0/2
    ww=sy(.5)# wall width
    ow=sy(3) # opening width
    x1=sx(1); y1=sy(20) # room ident display
    best=0
    player=utils.load_image('player.png',True)
    player_pale=utils.load_image('player_pale.png',True)
    player_w=player.get_width(); player_h=player.get_height()
    player_cx=x0+s0/2; player_cy=x0+s0/2; player_k=0
    player_ms=-1; direction=''
    wish_img=utils.load_image('wish.png',True); wish_x=sx(26.9); wish_y=sy(7.7)
    wish_glow=utils.load_image('wish_glow.png',True)
    wish_cxy=utils.top_left_to_centre(wish_img,(wish_x,wish_y))
    wish_current_img=wish_img; wish_ms=None
    bag_img=utils.load_image('bag.png',True); bag_x=sx(21); bag_y=sy(2)
    bag_full=utils.load_image('bag_full.png',True)
    bag_glow=utils.load_image('bag_glow.png',True)
    bag_current_img=bag_img; bag_ms=None; bag_full_ms=None
    bag_cxy=utils.top_left_to_centre(bag_img,(bag_x,bag_y))
    bag=[]
    door=utils.load_image('door.png',True)
    open_door=utils.load_image('open_door.png',True)
    window=utils.load_image('window.png',True)
    window_ladder=utils.load_image('window_ladder.png',True)
    room_ms=-1; room_delay=1000
    wishes=1
    floor=(228,201,172)
    objects=[]
    box_open=utils.load_image('box_open.png',True)
    box_closed=utils.load_image('box_closed.png',True)
    box_x=sx(7.8); y=sy(14.3)
    box_o_y=y-box_open.get_height(); box_c_y=y-box_closed.get_height()
    box_cxy=utils.top_left_to_centre(box_closed,(box_x,box_c_y))
    box_glow=utils.load_image('box_glow.png',True)
    box_current_img=box_closed; box_ms=None
    score=0
    score_c=(box_x+sy(2.7),y-sy(3.1))
    hole=utils.load_image('hole.jpg',False)
    green_hole=utils.load_image('green_hole.png',True)
    trap_x=0; trap_y=0; trap_ms=-1
    x=16; y=7.5; d=8; inside_bag_cxy=[]
    # items inside bag - centre positions
    xy=[(x,y),(x-d,y+d),(x+d,y+d),(x,y+d),(x-d,y),(x+d,y)]
    for (x,y) in xy:
        rx=random.randint(-4,4); ry=random.randint(-4,4)
        inside_bag_cxy.append((sx(x)+rx,sy(y)+ry))
    inside_bag=utils.load_image('inside_bag.png',True)
    bag_base=utils.load_image('bag_base.png',True)
    clouds=utils.load_image('clouds.jpg',False)
    casino_running=False
    casino_count=[]
    casino_delay=[]
    casino_ms=[]
    casino_obj=[None,None,None,None]
    t=[x0+sy(5.6),y0+sy(6.21),x0+sy(10.13),y0+sy(10.75)]
    casino_cxy=[(t[0],t[1]),(t[2],t[1]),(t[0],t[3]),(t[2],t[3])]
    token=utils.load_image('token.jpg',False)
    fuel=utils.load_image('fuel.png',True)
    health=9; health_c=(sx(29.4),sy(2.5)); health_imgs=[]
    laser_ms=None; gas_ms=None
    steal=utils.load_image('steal.png',True); steal_xy=(sx(12.61),sy(1.2))
    take_ms=None; steal_ms=None; take_delay=0
    telep_ms=None
    map1_grid=utils.load_image('map1_grid.png',True)
    w=sy(21.33); map1=pygame.Surface((w,w)); map1_d=w/4
    map1_xy=(sx(16)-2*map1_d,sy(.2)); map2=None
    d=map1_d*2; d2=int(d/2); map2_rect=(cx-d2,cy-d2,d,d)
    wishes3=False
    laser_map=utils.load_image('laser_map.jpg',False,'bgd')
    star=utils.load_image('star.png',True)
    state=1
    # 1=normal
    # 2=bag
    # 3=wish
    # 4=map

def sx(f): # scale x function
    return int(f*factor+offset+.5)

def sy(f): # scale y function
    return int(f*factor+.5)
