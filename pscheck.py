import psutil

def pscheck(seekitem):
    """ hi """
#    plist = list(psutil.process_iter())
    plist = psutil.process_iter()
    strl = " ".join(str(x) for x in plist)
    if seekitem in strl:
        print "requested process is running"

pscheck("System")
