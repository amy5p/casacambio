import os


BASE_PATH = os.getcwd()
BLACK_LIST = [__name__, "clearinstallfiles.py", "manage.py"]

def deletepy(path):
    for p in os.listdir(path):
        p = os.path.join(path, p)

        if os.path.isdir(p):
            deletepy(p)
        elif os.path.isfile(p):
            try:
                if (os.path.basename(p) in BLACK_LIST):
                    continue
                elif os.path.splitext(p)[1].lower() == ".py":
                    os.remove(p)
                    print("ELIMINADO:::: {}".format(p))
            except (BaseException) as e:
                print(e)
        else:
            pass



def gotopyc(path):
    for p in os.listdir(path):
        p = os.path.join(path, p)

        if os.path.isdir(p):
            if os.path.basename(p).lower() == "__pycache__":
                for name in os.listdir(p):
                    p2 = os.path.join(p, name)
                    if os.path.splitext(p2)[1].lower() == ".pyc":
                        f = open(p2, "rb")
                        data = f.read()
                        f.close()
                        new = os.path.basename(p2).split(".")[0] + ".pyc"
                        p3 = os.path.join(path, new)
                        f = open(p3, "wb")
                        f.write(data)
                        f.close()
                        print(p3)
            else:
                gotopyc(p)
                
            

        

deletepy(BASE_PATH)
gotopyc(BASE_PATH)
                    


                    
