# cas.py
import random,utils,g,pygame

#1 always entrance
room_names=['entrance','dark','ice','thieves','dungeon','laser','wizard','gas',\
            'treasure']
room_names4=['trapdoor','map','teleporter','pool','genie','vines','casino']
spell_names=('wish','2entrance','triple','health','opendoors')
obj_names=('goggles','skates','cloak','ladder','shield','gasmask')
obj_names4=('magic','fuel','snorkel','lamp','knife','token')
jewel_names=('ruby','sapphire','emerald','diamond')
corners=('NW','NE','SW','SE')
opposite={'N':'S','S':'N','E':'W','W':'E'}
helpers={'ice':'skates','vines':'knife','pool':'snorkel','gas':'gasmask',\
         'thieves':'cloak','trapdoor':'goggles','laser':'shield'}
wishes=[]

class Castle:
    def __init__(self,side): # 3x3 or 4x4
        self.side=side
        names=room_names+room_names4
        self.rooms=[] # room numbers
        n=1
        for r in range(1,side+1):
            for c in range(1,side+1):
                room=Room(n,names[n-1])
                if r==1: room.mate['N']=0; room.connect['N']=0 # 0=outside
                if r==side: room.mate['S']=0; room.connect['S']=0
                if c==1: room.mate['W']=0; room.connect['W']=0
                if c==side: room.mate['E']=0; room.connect['E']=0
                if room.mate['N']==None: room.mate['N']=n-side
                if room.mate['S']==None: room.mate['S']=n+side
                if room.mate['E']==None: room.mate['E']=n+1
                if room.mate['W']==None: room.mate['W']=n-1
                self.rooms.append(room)
                n+=1
        room=Room(n,'secret'); self.rooms.append(room)
        for d in 'NSEW': room.connect[d]=0
        self.current_room_n=1
        the_lot=spell_names+obj_names+jewel_names+jewel_names
        if side==4: the_lot+=obj_names4; # the_lot+=the_lot
        g.objects=[]; maxw=0; maxh=0
        for s in the_lot:
            obj=Object(s); g.objects.append(obj)
            w=obj.img.get_width(); h=obj.img.get_height()
            if w>maxw: maxw=w
            if h>maxh: maxh=h
        g.maxw=maxw; g.maxh=maxh
        for n in range(0,10):
            img=utils.load_image(str(n)+'.png',True,'health')
            g.health_imgs.append(img)

    # 0=outside, 1=open door, 2=closed door, 3=high window
    def setup(self):
        shuffle(self.rooms)
        self.make_map()
        for room in self.rooms:
            if room.connect['N']<>0: 
                r=random.randint(1,3)
                room.connect['N']=r; self.rooms[room.mate['N']-1].connect['S']=r
            if room.connect['W']<>0:
                r=random.randint(1,3)
                room.connect['W']=r; self.rooms[room.mate['W']-1].connect['E']=r
            for d in corners: room.corner[d]=None # empty corners
        room=self.rooms[0] # set up Entrance
        room.corner['NW']=name2obj('opendoors')
        room.connect['E']=1; self.rooms[room.mate['E']-1].connect['W']=1
        room.connect['S']=1; self.rooms[room.mate['S']-1].connect['N']=1
        # max 1 closed door per room
        for room in self.rooms:
            found=False
            for d in 'NSEW':
                if room.connect[d]==2:
                    if found:
                        room.connect[d]=1; opp=opposite[d]
                        self.rooms[room.mate[d]-1].connect[opp]=1
                    else:
                        found=True
        for ind in range(len(g.objects)): # distribute objects - one of each
            while True:
                name='treasure'
                while name in ('treasure','wizard','secret'): # keep empty
                    ind1=random.randint(0,len(self.rooms)-1)
                    room=self.rooms[ind1]; name=room.name
                ind2=random.randint(0,3); d=corners[ind2]
                if room.corner[d]==None:
                    obj=g.objects[ind]
                    if not self.is_obj_in_room(room,obj): room.corner[d]=obj
                    break
        room=self.rooms[15] # top up last room with diamomnds
        for corner in corners:
            if room.corner[corner]==None:
                room.corner[corner]=name2obj('diamond') 
        self.current_room=self.rooms[0]
        #self.new_room()### only necessary when debugging
        g.player_cx=g.x0+g.s0/2; g.player_cy=g.x0+g.s0/2
        pick=random.randint(1,5)
        if pick==1: dx=10.5; dy=3.5
        if pick==2: dx=2.5; dy=10.7
        if pick==3: dx=2.5; dy=3.5
        if pick==4: dx=10.5; dy=10.7
        if pick==5: dx=6.5; dy=7.1
        self.place_trap()
        g.trap_ms==-1
        g.wishes=1
        g.score=0
        g.bag=[]
        g.laser_ms=None; g.gas_ms=None; g.take_ms=None; g.steal_ms=None
        g.telep_ms=None
        g.health=9
        g.wishes3=False
        for ind in range(6): g.bag.append(None)

    def place_trap(self):
        hw=g.hole.get_width(); hh=g.hole.get_height()
        if random.randint(1,2)==1:
            y1=g.y0; y2=y1+g.s0-hh; g.trap_y=random.randint(y1,y2)
            g.trap_x=g.cx-hw/2
        else:
            x1=g.x0; x2=x1+g.s0-hw; g.trap_x=random.randint(x1,x2)
            g.trap_y=g.cy-hh/2
        
    def make_map(self):
        g.map1.fill(g.floor)
        ind=0; d=g.map1_d; d2=d/2
        y=0
        for r in range(4):
            x=0
            for c in range(4):
                room=self.rooms[ind]
                if room.name=='dark':
                    pygame.draw.rect(g.map1,utils.BLACK,(x,y,d,d))
                elif room.name=='laser':
                    g.map1.blit(g.laser_map,(x,y))
                elif room.name=='entrance':
                    cx=x+d2; cy=y+d2; img=g.box_closed
                    w=int(.4*img.get_width()); h=int(.4*img.get_height())
                    try:
                        img=pygame.transform.smoothscale(img,(w,h))
                    except:
                        img=pygame.transform.scale(img,(w,h))
                    utils.centre_blit(g.map1,img,(cx,cy))
                elif room.name=='map':
                    cx=x+d2; cy=y+d2
                else:
                    try:
                        img=pygame.transform.smoothscale(room.bgd,(d,d))
                    except:
                        img=pygame.transform.scale(room.bgd,(d,d))
                    g.map1.blit(img,(x,y))
                x+=d; ind+=1
            y+=d
        for i in range(2):
            try:
                img=pygame.transform.smoothscale(g.map1,(d2,d2))
            except:
                img=pygame.transform.scale(g.map1,(d2,d2))
            utils.centre_blit(g.map1,img,(cx,cy))
        g.map1.blit(g.map1_grid,(0,0))
        try:
            g.map2=pygame.transform.smoothscale(g.map1,(d*2,d*2))
        except:
            g.map2=pygame.transform.scale(g.map1,(d*2,d*2))

    def map_display(self):
        g.screen.fill(g.bgd_colour)
        x0=g.sx(1); y0=g.sy(6); d=g.sy(2.7)
        g.screen.blit(g.map2,(x0,y0))
        y=y0; ind=0
        for r in range(4):
            x=x0
            for c in range(4):
                if utils.mouse_in(x,y,x+d,y+d):
                    self.rooms[ind].display1(g.sx(13.5),g.sy(2))
                    return
                x+=d
                ind+=1
            y+=d
            
    def move(self,nsew):
        if nsew<>'':
            delay=50; dd=g.player_w/4
            if g.player_k>4: delay=20; dd=g.player_w/2
            keep_cx=g.player_cx; keep_cy=g.player_cy
            keep_room=self.current_room
            if g.trap_ms<>-1: return
            d=pygame.time.get_ticks()-g.player_ms
            if g.player_ms==-1 or d>delay:
                g.redraw=True
                kx=g.player_cx; ky=g.player_cy
                dx=0; dy=0
                if self.current_room.name=='ice' and not in_bag('skates'):
                    dd*=random.randint(10,40)
                if nsew=='N':dy=-dd
                elif nsew=='S':dy=dd
                elif nsew=='E':dx=dd
                elif nsew=='W':dx=-dd
                g.player_cx+=dx; g.player_cy+=dy; g.player_k+=1
                nsew=self.check_connects(nsew)
                if nsew<>'':
                    r=self.current_room; n=r.connect[nsew]
                    # 0=outside, 1=open door, 2=closed door, 3=high window
                    if n not in (0,2):
                        if n==1 or (n==3 and in_bag('ladder')):
                            self.move_through_connect(nsew)
                            self.new_room()
                self.keep_inside()
                if self.current_room.name=='trapdoor':
                    if g.trap_ms==-1:
                        x1=g.trap_x; y1=g.trap_y; d=g.hole.get_width()
                        x2=x1+d; y2=y1+d
                        if player_in(x1,y1,x2,y2):
                            g.player_cx+=dx*4; g.player_cy+=dy*4 # 1 more step :o)
                            g.trap_ms=pygame.time.get_ticks()
                g.player_ms=pygame.time.get_ticks()
                if self.current_room==keep_room:
                    name=self.current_room.name
                    ok=True
                    if name=='pool' and not in_bag('snorkel'): ok=False
                    if name=='vines' and not in_bag('knife'): ok=False
                    if not ok: g.player_cx=keep_cx; g.player_cy=keep_cy

    def keep_inside(self):
        x2=g.player_w/2; y2=g.player_h/2
        if g.player_cx<(g.xw+x2): g.player_cx=g.xw+x2
        elif g.player_cx>(g.xe-x2): g.player_cx=g.xe-x2
        elif g.player_cy<(g.yn+y2): g.player_cy=g.yn+y2
        elif g.player_cy>(g.ys-y2): g.player_cy=g.ys-y2

    def check_connects(self,direction):
        # allow for ice rink
        if g.player_cx>g.xe: g.player_cx=g.xe
        if g.player_cx<g.xw: g.player_cx=g.xw
        if g.player_cy>g.ys: g.player_cy=g.ys
        if g.player_cy<g.yn: g.player_cy=g.yn
        for v in 'NSEW':
            if v==direction:
                x1,y1,x2,y2=connect_box(v)
                if v in 'NS': d=g.player_h/2; y1-=d; y2+=d
                else: d=g.player_w/2; x1-=d; x2+=d
                if player_in(x1,y1,x2,y2): return v
        return ''

    def move_through_connect(self,nsew):
        r=self.current_room; m=r.mate[nsew]
        self.place_trap()
        self.current_room=self.rooms[m-1]
        x2=g.player_w/2; y2=g.player_h/2
        if nsew=='N': g.player_cy=g.ys-y2
        elif nsew=='S': g.player_cy=g.yn+y2
        elif nsew=='E': g.player_cx=g.xw+x2
        elif nsew=='W': g.player_cx=g.xe-x2

    def new_room(self):
        room=self.current_room; g.room_ms==-1
        if room.name=='treasure':
            ind=0
            for corner in corners:
                room.corner[corner]=name2obj(jewel_names[ind]); ind+=1
            self.close_doors()
        elif room.name=='wizard':
            for corner in corners: room.corner[corner]=rand_obj()
            self.close_doors()
        elif room.name=='dungeon':
            for d in 'NSEW':
                if room.connect[d]>0: room.connect[d]=3
            self.do_mates(room,3)
        elif room.name=='secret':
            ind=0
            for corner in corners:
                if room.corner[corner]==None:
                    spell=spell_names[ind]; room.corner[corner]=name2obj(spell)
                    ind+=1
                    if ind==1: ind=2

    def close_doors(self):
        room=self.current_room
        for d in 'NSEW':
            if room.connect[d]>0: room.connect[d]=2
        self.do_mates(room,2)
        
    def open_doors(self):
        room=self.current_room
        for d in 'NSEW':
            if room.connect[d]==2:
                room.connect[d]=1
                n=room.mate[d]
                if n>0: ind=n-1; rm=self.rooms[ind]; rm.connect[opposite[d]]=1
        
    def do_mates(self,room,v):
        for d in 'NSEW':
            n=room.mate[d]
            if n>0: ind=n-1; rm=self.rooms[ind]; rm.connect[opposite[d]]=v
        
    def update(self):
        if g.telep_ms<>None:
            d=pygame.time.get_ticks()-g.telep_ms
            if g.telep_ms==-1 or d>1500:
                ind=random.randint(0,16)
                if self.rooms[ind].name<>'teleporter':
                    self.current_room=self.rooms[ind]; self.new_room()
                    g.telep_ms=pygame.time.get_ticks()
                    g.redraw=True
        d=pygame.time.get_ticks()-g.room_ms
        r=self.current_room
        if g.room_ms==-1 or d>g.room_delay:
            if r.name=='wizard':
                g.redraw=True
                for corner in corners: r.corner[corner]=rand_obj()
            g.room_ms=pygame.time.get_ticks()
        if g.trap_ms<>-1:
            d=pygame.time.get_ticks()-g.trap_ms
            if d>1000:
                g.redraw=True
                for i in range(100):
                    ind=random.randint(0,16); rm=self.rooms[ind]
                    if rm.name<>'trapdoor': break
                self.current_room=rm; self.new_room(); g.trap_ms=-1
        if r.name=='laser' and not in_bag('shield'):
            if g.health>0:
                if g.laser_ms==None:
                    g.laser_ms=pygame.time.get_ticks()
                else:
                    if not self.check_all_black(r.bgd):
                        d=pygame.time.get_ticks()-g.laser_ms
                        if d>2000:
                            g.health-=1; g.laser_ms=pygame.time.get_ticks()
                            g.redraw=True
        else:
            g.laser_ms=None
        if r.name=='gas' and not in_bag('gasmask'):
            if g.health>0:
                if g.gas_ms==None:
                    g.gas_ms=pygame.time.get_ticks()
                else:
                    d=pygame.time.get_ticks()-g.gas_ms
                    if d>2000:
                        g.health-=1; g.gas_ms=pygame.time.get_ticks()
                        g.redraw=True
        else:
            g.gas_ms=None
        if r.name=='thieves' and not in_bag('cloak'):
            if g.take_ms==None:
                g.take_ms=pygame.time.get_ticks()
                g.take_delay=random.randint(6000,12000)
            else:
                d=pygame.time.get_ticks()-g.take_ms
                if d>g.take_delay:
                    if take_one():
                        g.take_ms=pygame.time.get_ticks()
                        g.steal_ms=pygame.time.get_ticks()
                        g.redraw=True
                    else:
                        g.take_ms=None
        if r.name<>'thieves': g.take_ms=None; g.steal_ms=None
        # glows
        if g.steal_ms<>None:
            d=pygame.time.get_ticks()-g.steal_ms
            if d>2500: g.steal_ms=None; g.redraw=True
        g.bag_current_img,g.bag_ms=\
            utils.glow(g.bag_img,g.bag_glow,g.bag_current_img,g.bag_ms,1000)
        g.bag_current_img,g.bag_full_ms=\
            utils.glow(g.bag_img,g.bag_full,g.bag_current_img,g.bag_full_ms,1000)
        g.wish_current_img,g.wish_ms=\
            utils.glow(g.wish_img,g.wish_glow,g.wish_current_img,g.wish_ms,2000)
        g.box_current_img,g.box_ms=\
            utils.glow(g.box_closed,g.box_glow,g.box_current_img,g.box_ms,2000)
        if r.name=='casino': self.casino_update()
                
    def check_all_black(self,img):
        w2=g.player_w/2; h2=g.player_h/2
        x1=g.player_cx-g.x0-w2; y1=g.player_cy-g.y0-h2
        y=y1
        for r in range(g.player_h):
            x=x1
            for c in range(g.player_w):
                col=img.get_at((x,y))
                if col[0]>10: return False
                x+=1
            y+=1
        return True
                
    def is_obj_in_room(self,room,obj): # eg (room obj,'lamp')
        for d in corners:
            if room.corner[d]==obj: return True
        return False

    def obj(self,name,corner): # eg obj('ice','NE')
        return self.room(name).corner[corner]

    def room(self,name): # eg room('ice')
        for room in self.rooms:
            if room.name==name: return room
        return none

    def pickup(self):
        if self.current_room.pickup(): return True
        if self.current_room.name=='map':
            rect=g.map2_rect
            x1=rect[0]; y1=rect[1]; x2=x1+rect[2]; y2=y1+rect[3]
            if player_in(x1,y1,x2,y2):
                g.state=4; return True
        return False

    def drop(self,obj):
        room=self.current_room
        if obj.name=='2entrance':
            self.current_room=self.rooms[0]; g.state=1; return True
        elif obj.name=='triple':
            if room.name=='entrance':
                g.score*=3; g.box_ms=-1; g.state=1; return True
            return False
        elif obj.name=='health':
            g.health=9; g.state=1; return True
        # 0=outside, 1=open door, 2=closed door, 3=high window
        elif obj.name=='opendoors':
            self.open_doors(); g.state=1; return True
        if room.name=='entrance' and obj.name in jewel_names:
            v=value(obj.name) ; g.score+=v
            g.box_ms=-1; g.state=1; return True
        # specials? eg lamp+genie
        if room.name=='teleporter' and obj.name=='fuel':
            g.telep_ms=-1; g.state=1; return True
        if room.name=='genie' and obj.name=='lamp' and not g.wishes3:
            g.wishes3=True; g.wishes+=3; g.wish_ms=-1; g.state=1; return True
        if room.name=='casino' and obj.name=='token':
            self.casino_start(); g.state=1; return True
        # room to drop?
        for d in corners:
            if room.corner[d]==None: # empty corner
                room.corner[d]=obj
                return True
        return False

    def wish_display(self):
        new=False
        if wishes==[]: new=True
        g.screen.blit(g.clouds,(g.sx(0),0))
        #g.screen.fill(g.bgd_colour)
        object_names=obj_names+('2entrance',)
        if self.side==4: object_names+=obj_names4
        cy=g.sy(4.5); dx=g.sy(8.5); dy=g.sy(7.5); ind=0
        for r in range(3):
            if r==2: cy-=g.sy(1)
            cx=g.sx(4)
            for c in range(4):
                if r==0:
                    if c<3: cx+=g.sy(1)
                    else: cx-=g.sy(3)
                name=object_names[ind]
                if name=='magic': ind+=1; name=object_names[ind]
                obj=name2obj(object_names[ind])
                utils.centre_blit(g.screen,obj.img0,(cx,cy))
                if new:
                    xy=utils.centre_to_top_left(obj.img0,(cx,cy))
                    wishes.append((obj,xy))
                cx+=dx
                ind+=1
                if ind==len(object_names): break
            cy+=dy
            if ind==len(object_names): break
        if new: wishes.reverse()

    def wish_click(self):
        for obj,xy in wishes:
            if utils.mouse_on_img(obj.img0,xy):
                ind=bag_free_ind()
                if ind==-1:
                    g.bag_full_ms=-1
                else:
                    g.bag[ind]=obj
                    g.wishes-=1
                    g.bag_ms=-1
                g.state=1; return
        g.state=1; return # empty space click

    def casino_start(self):
        g.casino_running=True
        g.casino_count=[]; g.casino_delay=[]
        for ind in range(4):
            g.casino_ms.append(-1)
            r=random.randint(20,37); g.casino_count.append(r)
            r=random.randint(100,200); g.casino_delay.append(r)
        self.casino_update()

    def casino_update(self):
        if g.casino_running:
            ms=pygame.time.get_ticks(); still_going=False
            for ind in range(4):
                if g.casino_count[ind]>0:
                    still_going=True
                    d=ms-g.casino_ms[ind]
                    if g.casino_ms==-1 or d>g.casino_delay[ind]:
                        g.redraw=True
                        r=random.randint(0,3)
                        g.casino_obj[ind]=name2obj(jewel_names[r])
                        g.casino_ms[ind]=ms
                        g.casino_count[ind]-=1
            if not still_going: self.casino_stop()

    def casino_stop(self):
        g.redraw=True
        g.casino_running=False
        room=self.current_room
        tally={'ruby':0,'sapphire':0,'emerald':0,'diamond':0}
        for ind in range(4):
            name=g.casino_obj[ind].name; tally[name]+=1
        for jewel in tally:
            if tally[jewel]==4: # 4jewels
                for corner in corners:
                    if room.corner[corner]==None:
                        room.corner[corner]=name2obj(jewel)
                return
            if tally[jewel]==3: # 3 jewels
                n=0
                for corner in corners:
                    if room.corner[corner]==None:
                        room.corner[corner]=name2obj(jewel); n+=1
                    if n==3: return
            if tally[jewel]==2: # 1 jewel
                for corner in corners:
                    if room.corner[corner]==None:
                        room.corner[corner]=name2obj(jewel); break

    def health_display(self):
        utils.centre_blit(g.screen,g.health_imgs[g.health],g.health_c)
        #utils.display_number(g.health,g.health_c,g.font2,utils.RED)

class Room:
    def __init__(self,n,name):
        self.n=n # room no.
        # neighbour room nos
        self.corner={'NW':None,'NE':None,'SW':None,'SE':None}
        self.connect={'N':None,'S':None,'E':None,'W':None}
        self.mate={'N':None,'S':None,'E':None,'W':None}
        self.name=name
        if name in ('gas','dark','thieves','teleporter','laser'):
            self.bgd=utils.load_image(name+'.png',True,'bgd')
        elif name in ('dungeon','pool','ice','vines','wizard','trapdoor'\
                      ,'treasure','genie','casino','secret'):
            self.bgd=utils.load_image(name+'.jpg',False,'bgd')
        else:
            self.bgd=None

    def display(self):
        if self.name=='dark':
            if not in_bag('lamp'):
                g.screen.fill((0,0,0),(g.x0,g.y0,g.s0,g.s0))
        else:
            if self.name in ('gas','dungeon','pool','ice','vines','teleporter'\
                             ,'wizard','trapdoor','treasure','genie','casino'\
                             ,'laser','secret'):
                g.screen.blit(self.bgd,(g.x0,g.y0))
            else:
                g.screen.fill(g.floor,(g.x0,g.y0,g.s0,g.s0))
                if self.name=='map':
                    utils.centre_blit(g.screen,g.map2,(g.cx,g.cy))
        if self.name=='dark' and not in_bag('lamp'):
            pass
        else:
            if self.name=='casino':
                casino_display()
            else:
                g.casino_running=False
            if self.name=='trapdoor':
                img=None
                if in_bag('goggles'): img=g.green_hole
                if g.trap_ms<>-1: img=g.hole
                if img<>None: g.screen.blit(img,(g.trap_x,g.trap_y))
            self.show_helper(self.name)
            for corner in corners: # objects
                top_left=self.obj_top_left(corner)
                if top_left<>None:
                    obj=self.corner[corner]; g.screen.blit(obj.img,top_left)
            if g.health>0:
                img=g.player
                if self.name=='thieves' and in_bag('cloak'): img=g.player_pale
                if g.telep_ms==None: # not teleporting
                    utils.centre_blit(g.screen,img,(g.player_cx,g.player_cy))
            if self.name in ('gas','dark','thieves'): # draw over objects
                g.screen.blit(self.bgd,(g.x0,g.y0))
            self.centre()
        if g.steal_ms<>None: g.screen.blit(g.steal,g.steal_xy)
        self.wall()
        # 0=outside, 1=open door, 2=closed door, 3=high window
        for v in 'NSEW':
            if self.connect[v]>0:
                colour=utils.BLACK
                if self.connect[v]==1: colour=utils.WHITE
                elif self.connect[v]==2: colour=(162,126,87)
                b=connect_box(v)
                pygame.draw.rect(g.screen,colour,(b[0],b[1],b[2]-b[0],b[3]-b[1]))
        #room name
        #utils.text_blit1(g.screen,self.name,g.font1,(g.x1,g.y1),utils.CREAM)
        
    def display1(self,x0,y0): # for map
        cx=x0+g.s0/2; cy=y0+g.s0/2; dx=x0-g.x0; dy=y0-g.y0
        if self.name=='dark':
            if not in_bag('lamp'):
                g.screen.fill((0,0,0),(x0,y0,g.s0,g.s0))
        else:
            if self.name in ('gas','dungeon','pool','ice','vines','teleporter'\
                             ,'wizard','trapdoor','treasure','genie','casino'\
                             ,'laser','secret'):
                g.screen.blit(self.bgd,(x0,y0))
            else:
                g.screen.fill(g.floor,(x0,y0,g.s0,g.s0))
                if self.name=='map':
                    utils.centre_blit(g.screen,g.map2,(cx,cy))
        if self.name=='entrance':
            utils.centre_blit(g.screen,g.box_closed,(cx,cy))
        if self.name=='dark' and not in_bag('lamp'):
            pass
        else:
            for corner in corners: # objects
                top_left=self.obj_top_left(corner)
                if top_left<>None:
                    x,y=top_left; x+=dx; y+=dy
                    obj=self.corner[corner]; g.screen.blit(obj.img,(x,y))
            if self.name in ('gas','dark','thieves'): # draw over objects
                g.screen.blit(self.bgd,(x0,y0))
        self.wall(dx,dy)
        # 0=outside, 1=open door, 2=closed door, 3=high window
        for v in 'NSEW':
            if self.connect[v]>0:
                colour=utils.BLACK
                if self.connect[v]==1: colour=utils.WHITE
                elif self.connect[v]==2: colour=(162,126,87)
                b=connect_box(v)
                pygame.draw.rect(g.screen,colour,(b[0]+dx,b[1]+dy,b[2]-b[0],b[3]-b[1]))
        
    # helpers={'ice':'skates'}
    def show_helper(self,room):
        if room in helpers:
            name=helpers[room]
            if in_bag(name): draw_obj(name)
            
    def wall(self,dx=0,dy=0):
        colour=(193,163,132); ww2=g.ww*2
        g.screen.fill(colour,(g.x0-g.ww+dx,g.y0-g.ww+dy,g.s0+ww2,g.ww))
        g.screen.fill(colour,(g.x0-g.ww+dx,g.y0+g.s0+dy,g.s0+ww2,g.ww))
        g.screen.fill(colour,(g.x0-g.ww+dx,g.y0-g.ww+dy,g.ww,g.s0+ww2))
        g.screen.fill(colour,(g.x0+g.s0+dx,g.y0-g.ww+dy,g.ww,g.s0+ww2))

    def centre(self): # displays entrances/objects if mouse over
        # 1=open door, 2=closed door, 3=high window
        if g.box_ms==None: # don't cover box glow
            for v in 'NSEW':
                img=None
                if self.connect[v]==1: img=g.open_door
                if self.connect[v]==2: img=g.door
                if self.connect[v]==3: img=g.window
                if img==g.window and in_bag('ladder'): img=g.window_ladder
                if img<>None:
                    b=connect_box(v)
                    if utils.mouse_in(b[0],b[1],b[2],b[3]):
                        utils.centre_blit(g.screen,img,(g.cx,g.cy)); return True
            for corner in corners:
                top_left=self.obj_top_left(corner)
                if top_left<>None:
                    obj=self.corner[corner]
                    if utils.mouse_on_img(obj.img,top_left):
                        img=obj.img0
                        if obj.name=='token': img=g.token
                        if obj.name=='fuel': img=g.fuel
                        utils.centre_blit(g.screen,img,(g.cx,g.cy))
                        if obj.name in jewel_names:
                            v=value(obj.name)
                            utils.display_number(v,(g.cx,g.cy),g.font2\
                                                 ,utils.CREAM,None,g.font3)
                        return True
        if self.name=='entrance':
            if utils.mouse_on_img(g.box_closed,(g.box_x,g.box_c_y)):
                g.screen.blit(g.box_open,(g.box_x,g.box_o_y))
                utils.display_number(g.score,g.score_c,g.font2,utils.CREAM)
            else:
                utils.centre_blit(g.screen,g.box_current_img,g.box_cxy)
            return True
        return False

    # eg obj_top_left('NE') -> top left (x,y) or None
    def obj_top_left(self,corner):
        obj=self.corner[corner]; xy=None; d=g.sy(.2)
        if obj<>None:
            if corner=='NW':xy=(g.x0+d,g.y0+d)
            elif corner=='NE':xy=(g.x0+g.s0-obj.img.get_width()-d,g.y0+d)
            elif corner=='SW':xy=(g.x0+d,g.y0+g.s0-obj.img.get_height()-d)
            elif corner=='SE':xy=(g.x0+g.s0-obj.img.get_width()-d,g.y0+g.s0-obj.img.get_height()-d)
        return xy

    def pickup(self):
        free_ind=bag_free_ind()
        for corner in corners:
            obj=self.corner[corner]
            if obj <> None: # corner has an object
                if corner=='NW': x1=g.x0; y1=g.y0
                elif corner=='NE':x1=g.x0+g.s0-g.maxw; y1=g.y0
                elif corner=='SW': x1=g.x0; y1=g.y0+g.s0-g.maxh
                elif corner=='SE': x1=g.x0+g.s0-g.maxw; y1=g.y0+g.s0-g.maxh
                x2=x1+g.maxw; y2=y1+g.maxh
                if player_in(x1,y1,x2,y2):
                    if obj.name=='wish':
                        self.corner[corner]=None; g.wishes+=1; g.wish_ms=-1
                        return True
                    if obj.name=='magic':
                        obj=None
                        for i in range(100):
                            ind=bag_free_ind()
                            if ind==-1: break # no more room
                            obj=rand_obj()
                            if not in_bag(obj.name):
                                if obj.name<>'magic': g.bag[ind]=obj
                        if obj==None: # bag already full
                            g.bag_full_ms=-1; return False
                        else:
                            self.corner[corner]=None; g.bag_ms=-1
                            return True
                    if free_ind<>-1:
                        g.bag[free_ind]=obj; self.corner[corner]=None
                        g.bag_ms=-1
                        return True
                    else:
                        g.bag_full_ms=-1
                        return False
        return False
    
class Object:
    def __init__(self,s):
        self.name=s
        self.img=utils.load_image(s+'.png',True,'objects')
        self.img0=utils.load_image(s+'.png',True,'objects0')
        for room,obj in helpers.iteritems():
            if  obj==s:
                self.img_pale=utils.load_image(s+'.png',True,'objects_pale')
                break

def shuffle(rms): #leave 0&16, shuffle name & bgd only
    l2=len(rms)-2
    for i in range(100):
        r1=random.randint(1,l2); r2=random.randint(1,l2)
        name=rms[r1].name; bgd=rms[r1].bgd
        rms[r1].name=rms[r2].name; rms[r1].bgd=rms[r2].bgd
        rms[r2].name=name; rms[r2].bgd=bgd

def connect_box(nsew):
    s2=g.s0/2; o2=g.ow/2
    if nsew=='N':
        cx=g.x0+s2; x1=cx-o2; x2=cx+o2; y1=g.y0-g.ww; y2=g.y0
    elif nsew=='S':
        cx=g.x0+s2; x1=cx-o2; x2=cx+o2; y1=g.y0+g.s0; y2=g.y0+g.s0+g.ww
    elif nsew=='W':
        cy=g.y0+s2; y1=cy-o2; y2=cy+o2; x1=g.x0-g.ww; x2=g.x0
    elif nsew=='E':
        cy=g.y0+s2; y1=cy-o2; y2=cy+o2; x1=g.x0+g.s0; x2=g.x0+g.s0+g.ww
    return (x1,y1,x2,y2)

def player_in(x1,y1,x2,y2):
    mx,my=g.player_cx,g.player_cy
    if x1>(mx+2): return False
    if x2<(mx-2): return False
    if y1>(my+2): return False
    if y2<(my-2): return False
    return True

def in_bag(name):
    for obj in g.bag:
        if obj<>None:
            if obj.name==name: return True
    return False
    
def rand_obj():
    for i in range(100):
        n=len(g.objects)
        r=random.randint(0,n-1)
        if g.objects[r].name not in spell_names: break
    return g.objects[r]

def name2obj(name):
    for obj in g.objects:
        if obj.name==name: return obj
    return None

def draw_obj(name):
    obj=name2obj(name)
    utils.centre_blit(g.screen,obj.img_pale,(g.cx,g.cy))

def bag_free_ind():
    for ind in range(6):
        if g.bag[ind]==None: return ind
    return -1

def take_one():
    for ind in range(6):
        if g.bag[ind]<>None: g.bag[ind]=None; return True
    return False

def casino_display():
    if g.casino_obj[0]<>None:
        for ind in range(4):
            utils.centre_blit(g.screen,g.casino_obj[ind].img,g.casino_cxy[ind])
            
def value(jewel0):
    v=1
    for jewel in jewel_names:
        if jewel==jewel0: return v
        v+=1
    return 0

        


 

