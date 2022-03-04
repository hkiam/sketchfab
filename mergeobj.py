import sys
import re
import struct
''' merge & converts (some) obj files to stl
    python mergeobj.py path/to/file/filepattern*.obj path/to/write/output.stl
'''

def sub3V(a, b):
    return (
        a[0] - b[0],
        a[1] - b[1],
        a[2] - b[2],
    )
def cross3V(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )

class STLFile():
    BINARY_HEADER = 80

    def __init__(self):
        self.name = "unnamed"
        self.data = []

    def add(self, data):
        file = OBJFile()
        file.load(data)
        self.data.append(file)
        
    def save(self, fname):
        # an stl binary file is
        # - 80 bytes of description
        # - 4 bytes of size (unsigned int)
        # - size triangles :
        #
        #   - 12 bytes of normal
        #   - 9 * 4 bytes of coordinate (3*3 floats)
        #   - 2 bytes of garbage (usually 0)   
        # 
        #   REAL32[3] – Normal vector             - 12 bytes
        #   REAL32[3] – Vertex 1                  - 12 bytes
        #   REAL32[3] – Vertex 2                  - 12 bytes
        #   REAL32[3] – Vertex 3                  - 12 bytes
        #   UINT16    – Attribute byte count      -  2 bytes
        # 
        #      
        with open(fname,"wb") as f:
            f.write(bytes(self.name.ljust(self.BINARY_HEADER),"ascii"))
            f.write(struct.pack('<I', self.getNumFaces()))            
            for obj in self.data:                
                for face in obj.faces:
                    #v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
                    # write normal - 12 bytes                    
                    facenormal = self.calculateTriangleNormal(obj.normales[int(face[0][2])-1],obj.normales[int(face[1][2])-1],obj.normales[int(face[2][2])-1])
                    self.writefloatarray(f,facenormal)

                    # write Vertex 1 4 bytes
                    self.writefloatarray(f,obj.vertices[int(face[0][0])-1])
                    # write Vertex 2 4 bytes
                    self.writefloatarray(f,obj.vertices[int(face[1][0])-1])
                    # write Vertex 3 4 bytes
                    self.writefloatarray(f,obj.vertices[int(face[2][0])-1])

                    # write Attribute byte count 
                    f.write(b"\x00\x00")
                f.flush()
                                        
    def writefloatarray(self,file,data):
        for e in data:
            file.write(struct.pack('<f',e))

    def calculateTriangleNormal(self, v1, v2, v3):  
        a = sub3V(v2,v1)
        b = sub3V(v3,v1)
        n = cross3V(a, b)
        return n
        
    def getNumFaces(self):
        ret = 0
        for e in self.data:
            ret+=len(e.faces)
        return ret


class OBJFile():
    def __init__(self):
        self.name = "unnamed"    
        self.vertices = []
        self.normales = []
        self.textures = []
        self.faces = []    

    def load(self,fname):        
        with open(fname,"rt") as f:
            for line in f:
                oname = re.match("^o (.*)", line)
                if oname is not None:
                    print("currentObj " + oname[1])
                    name = oname[1].strip()
                    continue;
                #v -23.781757354736328 92.39582824707031 -105.84521484375 
                vertice = re.match("^v ([^ ]+) *([^ ]+) *([^ ]+)", line)
                if vertice is not None:
                    #print("v %f %f %f " % (float(vertice[1]),float(vertice[2]),float(vertice[3])))
                    self.vertices.append([float(vertice[1]),float(vertice[2]),float(vertice[3]) ])
                    continue;

                #vn -23.781757354736328 92.39582824707031 -105.84521484375 
                normal = re.match("^vn ([^ ]+) *([^ ]+) *([^ ]+)", line)
                if normal is not None:
                    #print("vn %f %f %f " % (float(normal[1]),float(normal[2]),float(normal[3]) ))
                    self.normales.append([float(normal[1]),float(normal[2]),float(normal[3]) ])
                    continue;

                #vn -23.781757354736328 92.39582824707031 
                texture = re.match("^vt ([^ ]+) *([^ ]+)", line)
                if texture is not None:
                    #print("vn %f %f %f " % (float(texture[1]),float(texture[2])))
                    self.textures.append([float(texture[1]),float(texture[2])])
                    continue;

                #f 1233/1233/1233 1231/1231/1231 1238/1238/1238
                #f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
                #f v1//vn1 v2//vn2 v3//vn3
                face = re.match("^f ([^ ]+) *([^ ]+) *([^ ]+)", line)
                if face is not None:
                    self.faces.append([face[1].split("/"),face[2].split("/"),face[3].split("/") ])                    
                    continue;                


infiles = sys.argv[1:-1]
outfile = sys.argv[-1]

stlfile = STLFile()
for f in infiles:
    stlfile.add(f)

stlfile.save(outfile)
