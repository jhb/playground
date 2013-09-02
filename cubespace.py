import random, time, sys

positionmap = {}
i = 0
for z in range(0,3):
    for y in range(0,3):
        for x in range(0,3):
            positionmap[i]=(x,y,z)
            i+=1
print positionmap

class TooFull(Exception):
    pass

class CubeBase(object):

    def get_path(self):
        path = []
        obj = self
        while obj.parent:
            path.insert(0,obj.id_in_parent)
            obj = obj.parent
        return path            

    def set_position(self):
        #import ipdb; ipdb.set_trace()
        if self.parent:
            path = [self]
            obj = self
            while obj.parent:
                path.insert(0,obj.parent)
                obj = obj.parent

            position = [0,0,0]
            for obj in path:
                if obj.id_in_parent:
                    cubepos = positionmap[obj.id_in_parent]
                else:
                    cubepos = (0,0,0)
                for axis in range(0,3):
                    position[axis] += cubepos[axis]*3**obj.dimension

            self.position=position

 
class Cube(CubeBase):
    
    length=3
    numslots=27
    maxfill1=7
    maxfillx=5

    def __init__(self,dimension,parent=None,id_in_parent=None,startcube=None,position=(0,0,0)):
        self.dimension=dimension
        self.parent=parent
        self.id_in_parent=id_in_parent
        self.position=position
        self.slots={}
        self.current = None
        self.set_position()
        if startcube:
            id = self.next_slot_id()
            self.slots[id]=startcube
            startcube.parent = self
            startcube.id_in_parent=id

        if dimension>1:
            id = self.next_slot_id()
            newcube = Cube(self.dimension-1,self,id)
            self.slots[id]=newcube
            self.current=newcube
            

    def next_slot_id(self):
        keys = self.slots.keys()
        available=[i for i in range(0,self.numslots) if i not in keys]
        return random.sample(available,1)[0]

        

    def add_content(self,content):
        if self.dimension==1:
            if len(self.slots)<=self.maxfill1:
                id = self.next_slot_id()
                container = Container(self,id,content)
                self.slots[id]=container
                self.current=container
                print container.get_path()
                return self,container
            else:
                raise TooFull
        else:
            try:
                outer,container=self.current.add_content(content)
                return self,container
            except TooFull:
                if len(self.slots)<=self.maxfillx:
                    id = self.next_slot_id()
                    cube = Cube(self.dimension-1,self,id)
                    self.slots[id]=cube
                    self.current = cube
                    outer,container=cube.add_content(content)
                    return self,container
                else: 
                    raise TooFull
        
class Container(CubeBase):
    
    def __init__(self,parent,id_in_parent,content,position=(0,0,0)):
        self.parent=parent
        self.id_in_parent=id_in_parent
        self.content=content
        self.position=position
        self.dimension=0
        self.set_position()
        self.set_color()

    def set_color(self):
        colors = []
        for i in range(0,1):
            color = []
            for i in range(0,3):
                color.append(random.randint(0,256))
            colors.append(color)
        self.colors=colors

class CubeSpace(object):

    def __init__(self):
        self.cube = Cube(1)
        self.containers = []

    def add_content(self,content):
        try:
            cube,container = self.cube.add_content(content)
        except TooFull:
            self.cube = Cube(self.cube.dimension+1,startcube=self.cube)
            cube,container = self.cube.add_content(content)
        self.containers.append(container)




if __name__=='__main__':

    cs = CubeSpace()
    for i in range(0,10000):
        print i
        if i==-1: import ipdb; ipdb.set_trace()
        cs.add_content('content%s'%i)
        print '----------------'

    def printcube(cube,indent):
        count = 0
        print
        for k,v in cube.slots.items():
            if isinstance(v,Cube) and v:
                if v.dimension>1:
                    print indent, k, 
                    printcube(v,indent+'   '),
                else:
                    print indent,k,len(v.slots),'containers'
        
    #printcube(cs.cube,'')

    #sys.exit()
    from visual import *
    scene=display(width=800,height=600,ambitient=1)
    #import ipdb; ipdb.set_trace()
    for container in cs.containers:
        print "_",['%02s'% p for p in container.get_path()],"_",container.position
        color = container.colors[0]
        mycolors = [i/255.0 for i in color]
        b = box(pos=container.position,length=0.5,height=0.5,width=0.5,color=mycolors)
        time.sleep(0.01)
