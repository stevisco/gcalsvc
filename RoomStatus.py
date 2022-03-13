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
    
 

    def __str__(self): 
        return self.__dict__.__str__()


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
