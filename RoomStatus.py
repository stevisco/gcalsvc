class RoomStatus:
    
    BUSY=1
    FREE=0                        

    
    def __init__(self):
        self.busynow=self.FREE 
        self.curevmsg = "unknown" 
        self.curevend ="" 
        self.curevstart ="" 
        self.curevtm =""
        self.nextevmsg = ""
        self.nextevstart=""
        self.nextevtm = ""
        self.nextevend=""
        self.metadata={}
    
 

    def __str__(self): 
        return self.__dict__.__str__()


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.busynow==other.busynow \
                and self.curevmsg==other.curevmsg \
                and self.curevstart==other.curevstart \
                and self.curevend==other.curevend \
                and self.curevtm==other.curevtm \
                and self.nextevtm==other.nextevtm \
                and self.nextevstart==other.nextevstart \
                and self.nextevend==other.nextevend \
                and self.nextevmsg==other.nextevmsg
        else:
            return False
