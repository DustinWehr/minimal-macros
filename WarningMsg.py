class WarningMsg:
    delivered = set()

    def __init__(self,x,*args):
        if x not in WarningMsg.delivered:
            print(x,args)
        WarningMsg.delivered.add(x)