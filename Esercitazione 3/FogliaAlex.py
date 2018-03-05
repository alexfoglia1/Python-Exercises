class DVRouting:
    def __init__(self,dvlist):
        self.n_node=len(dvlist)
        if not self.isConsistent(dvlist):
            raise Exception("Not symmetrical costs")
        if not self.checkAutolink(dvlist):
            raise Exception("Non-zero autolink cost")
        self.dvMatrix=list()
        self.dvList=dvlist
        self.stable=True
        for dict in dvlist:
            if len(dict.keys())!=0:
                self.stable=False
        for row in dvlist:
            for key in row.keys():
                if(row[key]<0):
                    raise Exception("Cannot set negative weight")
                
                
        
        for i in range(0,self.n_node):
            act_row=list()
            for j in range(0,self.n_node):
                if(i==j):
                    act_row.append(0)
                else:
                    act_row.append(None)
            self.dvMatrix.append(act_row)

    def checkAutolink(self,dvlist):
        for Dict in dvlist:
            for key in Dict:
                if key==dvlist.index(Dict) and Dict[key]!=0:
                    return False
        return True

    def isConsistent(self,dvlist):

                
        for i in range(0,len(dvlist)):
            for j in range(0,len(dvlist[i])):
                if(i!=j):
                    try:
                        if(dvlist[i][j]!=dvlist[j][i]):
                            return False
                    except:
                        continue
        return True
    def weight(self,x,y):
        if(x==y):
            return 0
        elif(x>=self.n_node or y>=self.n_node):
            return None
        try:
            weight=self.dvList[x][y]
            return weight
        except:
            return None
   
    def set(self,x,y,w):
        if w is None and x!=y:
            self.dvList[x][y]=None
            self.dvList[y][x]=None

        elif(w<0 or x>=self.n_node or y>=self.n_node  or (x==y and w!=0)):
            raise Exception
        else:
            self.dvList[x][y]=w
            self.dvList[y][x]=w

            self.stable=False

    def add(self):
        new_node={} 
        for i in range(0,self.n_node):
            new_node[i]=None

        self.dvList.append(new_node)
        new_row=list()
        for i in range(0,self.n_node):
            new_row.append(None)
            self.dvMatrix[i].append(None)
        new_row.append(0)
        self.dvMatrix.append(new_row)
        self.n_node=self.n_node+1
        indexof_newnode=self.n_node-1
        for dictz in self.dvList:
            dictz[indexof_newnode]=None
        
        return indexof_newnode
    def remove(self,x):
        if(x>=0 and x<self.n_node):
            for i in range (self.n_node):
                self.dvList[x][i]=None
                self.dvList[i][x]=None
        self.stable=False

    def setdv(self,dvlist):
        if(len(dvlist)!=len(self.dvList)):
            raise Exception
        self.dvMatrix=dvlist
        self.stable=False

    def getdv(self,x):
        if(x<0 or x>=self.n_node):
            return None
        return self.dvMatrix[x]
    def isNone(self):
        for i in range(0,self.n_node):
            for j in range(self.n_node):
                if(j!=i and self.dvMatrix[i][j]!=None):
                    return False
        return True
    def firstrefresh(self):
        for i in range(self.n_node):
            for j in range(self.n_node):
                if(i!=j):
                    try:
                        self.dvMatrix[i][j]=self.dvList[i][j]
                    except:
                        continue
    def step(self):
        if(self.isNone()):
            self.firstrefresh()
        
        temp_matrix=self.clonaMatrice(self.dvMatrix)
        for node in range(self.n_node):
            for other_node in range(self.n_node):
                new_dv=list()
                if(node==other_node):
                    continue
                else:
                    weight=list()
                    target=self.dvList[node]
                    for key in target.keys():
                        if(key!=node and self.dvMatrix[key][other_node] != None and target[key]!=None):
                            weight=weight+[self.dvMatrix[key][other_node]+target[key]]
                        
                        
                    if(weight==[]):
                        continue
                    else:
                        new_dv=weight 
                temp_matrix[node][other_node]=min(new_dv)
                
        
        self.stable=self.mat_equals(temp_matrix, self.dvMatrix, self.n_node)
        self.dvMatrix=temp_matrix
        return self.isstable()

        
    
    def mat_equals(self,mat1,mat2,llen):
        for i in range(llen):
            for j in range(llen):
                if(mat1[i][j]!=mat2[j][i]):
                    return False
        return True                  
    def clonaMatrice(self,matrix):
        clonata=list()
        length=len(matrix)
        for i in range(0,length):
            new_line=list()
            for j in range(0,length):
                new_line.append(matrix[i][j])
            clonata.append(new_line)
        return clonata
                
        
    def isstable( self ):
        return self.stable
    
    def compute(self):
        count=0
        while(True):
		  if(!self.step()):
			count=count+1
		  else
			break            
        return count+1
        
    def ordina(self,tuplelist):
        for i in range(0,len(tuplelist)):
            for j in range(i+1,len(tuplelist)):
                if tuplelist[i][1]>tuplelist[j][1]:
                    temp=tuplelist[i]
                    tuplelist[i]=tuplelist[j]
                    tuplelist[j]=temp
        
                    
                    
    
    

    def route(self,x,y):
        if(x<0 or x>=self.n_node):
            print "Node x > n node"
            return None
        elif (x==y):
            return (0,x)
        
        elif(y<0 or y>=self.n_node):
            print "Node y > n node"
            return None
        elif(self.dvMatrix[x][y]==None):
            
            return None
        else:
            pathsc=list()
            for z in range (self.n_node):
                if(z!=x and z!=y):
                    
                    xz=self.dvMatrix[x][z]
                    zy=self.dvMatrix[z][y]
                    if(xz is None or zy is None):
                        xzy=float('inf')
                    else:
                        xzy=xz+zy
                    pathsc.append((z,xzy))

                
        self.ordina(pathsc)
        
        #print pathsc
        target=pathsc[0]
        
        if(self.weight(x,y)<target[1] and not self.weight(x,y) is None):
            target=(y,self.weight(x,y))       
        return target          


            
            
        