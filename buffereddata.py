# (c) 2018 by Joerg Baach, License GPLv3

import mmap
import os
import struct
import io


class BytesBuffer(object):

    def __init__(self,bytes=b''):
        self.b = io.BytesIO(bytes)

    def __getattr__(self,name):
        return getattr(self.b,name)

    def resize(self,size):
        self.b.truncate(size)

    def size(self):
        self.b.getbuffer().nbytes



class MMBuffer(object):

    def __init__(self,fname):
        self.false = struct.Struct('?').pack(False)
        if not os.path.isfile(fname):
            f = open(fname,'wb')
            f.write(self.false)
            f.close()
        self.f = open(fname, 'r+b')
        self.b = mmap.mmap(self.f.fileno(),0)

    def __getattr__(self,name):
        return getattr(self.b,name)

    def close(self):
        self.b.close()
        self.f.close()



class BufferedData(object):

    def __init__(self,buffer,format):
        format = '?'+format
        self.struct = struct.Struct(format)
        self.false = struct.Struct('?').pack(False)
        self.bool = struct.Struct('?')
        self.linelength = self.struct.size
        self.deleted = []
        self.buffer = buffer

        if self.buffer.size()<self.linelength:
            self.buffer.resize(self.linelength)

        #print('scanning deleted positions for')
        pos = 0
        s = self.size()
        while pos < s:
            self.buffer.seek(pos)
            d = self.bool.unpack(self.buffer.read(1))[0]
            if not d:
                self.deleted.append(int(pos/self.linelength))
            pos+=self.linelength
        self.buffer.seek(0)


    def write(self,*data):
        if not self.deleted:
            self.buffer.seek(0,2)
            self.buffer.resize(self.size()+self.linelength)
            id = self.buffer.tell()/self.linelength
        else:
            id = self.deleted.pop(0)
            self.buffer.seek(id*self.linelength)
        self.buffer.write(self.struct.pack(1,*data))
        return id

    def read(self,id):
        offset = id*self.linelength
        self.buffer.seek(offset)
        line = self.struct.unpack(self.buffer.read(self.linelength))
        if line[0]:
            return line[1:]
        else:
            raise Exception('deleted')

    def update(self,id,*data):
        self.buffer.seek(id*self.linelength)
        self.buffer.write(self.struct.pack(1,*data))

    def delete(self,id):
        self.buffer.seek(id*self.linelength)
        self.buffer.write(self.false)
        self.deleted.append(id)

    def size(self):
        return self.buffer.size()

    def close(self):
        self.buffer.close()



if __name__ == "__main__":
    fname = 'testdata.txt'

    #os.unlink(fname)

    #f1 = MappedFile(BytesBuffer(),'hhl')
    f1 = BufferedData(MMBuffer(fname), 'hhl')

    print(f1.struct.size)
    f1.write(1,2,3)
    f1.write(4,5,6)
    f1.write(7,8,9)
    print(f1.size())
    f1.update(1,4,5,5)
    f1.delete(1)
    print(f1.write(9,9,9))
    print(f1.read(1))
    print(f1.size())
    f1.close()