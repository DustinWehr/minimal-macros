class WarningMsg:
    delivered = set()

    def __init__(self,x,*args):
        if x not in WarningMsg.delivered:
            print(x,args)
            print("This warning won't be printed again till restart program")
        WarningMsg.delivered.add(x)