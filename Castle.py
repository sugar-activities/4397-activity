#!/usr/bin/python
# Castle.py
"""
    Copyright (C) 2010  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,cas,utils,gtk,sys,buttons

class Castle:

    def __init__(self):
        self.best=0
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        if g.state==1: # normal
            g.screen.fill(g.bgd_colour)
            self.castle.current_room.display()
            self.castle.health_display()
            utils.centre_blit(g.screen,g.bag_current_img,g.bag_cxy)
            if g.wishes>0:
                utils.centre_blit(g.screen,g.wish_current_img,g.wish_cxy)
                x=g.wish_x; y=g.wish_y
                utils.display_number(g.wishes,(x+g.sy(2.2),y+g.sy(.9)),g.font1)
            buttons.draw()
            if g.best>0:
                x=g.sx(16); y=g.sy(20)
                utils.text_blit1(g.screen,str(g.best),g.font1,(x,y),(255,128,255))
                x-=g.sy(1.5); y-=g.sy(.3)
                g.screen.blit(g.star,(x,y))
        elif g.state==2: # inside bag
            grey=180; g.screen.fill((grey,grey,grey))
            utils.centre_blit(g.screen,g.bag_base,(g.sx(16),g.sy(11.2)))
            ind=0
            for obj in g.bag:
                if obj<>None:
                    utils.centre_blit(g.screen,obj.img0,g.inside_bag_cxy[ind])
                ind+=1
            g.screen.blit(g.inside_bag,(g.sx(0),g.sy(0)))
        elif g.state==3: # wishes
            self.castle.wish_display()
        elif g.state==4: # map
            self.castle.map_display()

    def click(self):
        if g.state==1:
            if self.castle.current_room.name=='map':
                if utils.mouse_in_rect(g.map2_rect):
                    g.state=4
                    return True
            if utils.mouse_on_img(g.bag_img,(g.bag_x,g.bag_y)):
                g.state=2
                return True
            if g.wishes>0:
                x=g.wish_x; y=g.wish_y
                if utils.mouse_on_img(g.wish_current_img,(x,y)):
                    g.state=3
                    return True
        elif g.state==2: # inside bag
            for ind in range(5,-1,-1): # reverse order to display
                obj=g.bag[ind]
                if obj<>None:
                    (cx,cy)=g.inside_bag_cxy[ind];
                    x=cx-obj.img0.get_width()/2; y=cy-obj.img0.get_height()/2
                    if utils.mouse_on_img(obj.img0,(x,y)):
                        if self.castle.drop(obj):
                            g.bag[ind]=None; return True
                        return False
            g.state=1; return True
        elif g.state==3: # wishes
            self.castle.wish_click()
        elif g.state==4: # map
            g.state=1; return True

    def bu_setup(self):
        self.bu={'N':None,'S':None,'E':None,'W':None, 'X':None}
        x0=g.sx(23.2); y0=g.sy(15.8); dx=g.sy(2.2); dy=dx
        for v in 'NSEWX':
            if v=='N': x=x0; y=y0-dy
            if v=='S': x=x0; y=y0+dy
            if v=='E': x=x0+dx; y=y0
            if v=='W': x=x0-dx; y=y0
            if v=='X': x=x0; y=y0
            self.bu[v]=buttons.Button(v,(x,y),True)
        buttons.Button('new',(g.sx(30),g.sy(20)),True)

    def bu_clear(self):
        for bu in 'NSEW':
            self.bu[bu].stay_down=False
        g.direction=''; g.player_k=0

    def bus_off(self):
        for v in 'NSEWX': self.bu[v].off()

    def bus_on(self):
        for v in 'NSEWX': self.bu[v].on()

    def do_key(self,key):
        d={pygame.K_UP:'N',pygame.K_DOWN:'S',\
           pygame.K_RIGHT:'E',pygame.K_LEFT:'W',pygame.K_SPACE:'X'}
        try:
            k=d[key]
        except:
            return
        if k=='X':
            if g.telep_ms<>None:
                g.telep_ms=None # stop teleporting
            else:
                self.castle.pickup()
        else: g.direction=k; g.player_ms=-1

    def do_button(self,bu):
        if bu in 'NSEW':
            g.player_ms=-1
        elif bu=='X':
            self.castle.pickup()
        elif bu=='new':
            self.castle.setup(); self.bus_on()

    def run(self):
        g.init()
        g.journal=self.journal
        if not self.journal:
            utils.load(); self.best=g.best
        else:
            g.best=self.best
        self.castle=cas.Castle(4) # 4x4 - 3x3 is ok too
        self.castle.setup()
        self.bu_setup()
        going=True
        while going:
            ms=pygame.time.get_ticks()
            g.mx,g.my=pygame.mouse.get_pos()
            # Pump GTK messages.
            while gtk.events_pending():
                gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==2: # centre button
                        g.version_display=not g.version_display; break
                    if g.state==1:
                        if g.telep_ms<>None:
                            g.telep_ms=None; break # stop teleporting
                        bu=buttons.check() 
                        if bu!='': self.do_button(bu); break
                    if g.health>0: self.click()
                elif event.type == pygame.MOUSEBUTTONUP:
                    g.redraw=True
                    if event.button==1:
                        self.bu_clear()
                elif event.type == pygame.KEYDOWN:
                    if g.direction=='': self.do_key(event.key)
                elif event.type == pygame.KEYUP:
                    g.redraw=True
                    self.bu_clear()
            if not going: break
            self.castle.move(g.direction)
            self.castle.update()
            if g.health==0: self.bus_off()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                if g.my>g.pointer.get_height():
                     g.screen.blit(g.pointer,(g.mx,g.my))
                pygame.display.flip()
                g.redraw=False
            if g.best<g.score: g.best=g.score
            self.best=g.best
            g.clock.tick(40)
            d=pygame.time.get_ticks()-ms; g.frame_rate=int(1000/d)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((800,600))
    game=Castle()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
