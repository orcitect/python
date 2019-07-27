""" resource monitor - disk, ram, swap """

import subprocess
from socket import gethostname
import smtplib
from email.mime.text import MIMEText
import time


def test_str_as_int(_s):
    """ hi """
    try:
        _ = int(_s)
        return True
    except ValueError:
        return False


def diskfree():
    """
        returns a 4-tuple x such that:
        x[0] = total disk on mountpoint /
        x[1] = used disk on mountpoint /
        x[2] = free disk on mountpoint /
        x[3] = percentage used on mountpoint /
    """
    tmp = subprocess.Popen(["diskfree", "/"], stdout=subprocess.PIPE)
    tmp.wait()
    out = tmp.communicate()
    cnt = 0
    total = 0
    used = 0
    freespace = 0

    for word in out.split():
        if test_str_as_int(word):
            if cnt == 0:
                total = int(word)
            elif cnt == 1:
                used = int(word)
            elif cnt == 2:
                freespace = int(word)
            cnt += 1
    total = used+freespace
    percent = (float(used)/(total))*100
    return (total, used, freespace, percent)


def freespace():
    """
        returns an 8-tuple:
        x[0] = total amount of physical RAM in KB
        x[1] = current amount of used RAM in KB
        x[2] = current amount of free RAM in KB
        x[3] = current amount of used disk cache in KB
        x[4] = current amount of free disk cache in KB
        x[5] = total system swap in KB
        x[6] = current amount of used swap in KB
        x[7] = current amount of free swap in KB
    """
    tmp = subprocess.Popen(["freespace"], stdout=subprocess.PIPE)
    tmp.wait()
    out = tmp.communicate()
    stats = [[0]*7 for _x in range(4)]

    lnr = 0
    for line in out.split("\n"):
        wnr = 0
        for word in line.split():
            if test_str_as_int(word):
                stats[lnr][wnr] = int(word)
            else:
                stats[lnr][wnr] = 0
            wnr += 1
        lnr += 1
    m_tot = stats[1][1]
    m_used = stats[1][2]
    m_free = stats[1][3]
    c_used = stats[2][2]
    c_free = stats[2][3]
    s_tot = stats[3][1]
    s_used = stats[3][2]
    s_free = stats[3][3]
    return (m_tot, m_used, m_free, c_used, c_free, s_tot, s_used, s_free)


class Data:
    def __init__(self):
        """  a function """
        servername = gethostname().upper()
        warn_disk_free = 78         # Lower limit for sending low disk space warning (in %)
        crit_disk_free = 85         # Lower limit for senidng critically low disk space warning (in %)
        warn_filecache = 1024       # Upper limit for sending low filecache warning (in KB)
        crit_filecache = 512        # Upper limit for sending critically low filecache warning (in KB)
        warn_swap = 128*1024        # Upper limit for sending low swap warning (in KB)
        crit_swap = 64*1024         # Upper limit for sending critically low swap warning (in KB)

        disk_total, disk_used, disk_free, disk_percent = diskfree()
        mem_total, mem_used, mem_free, cache_used, cache_free, swap_total, swap_used, swap_free = freespace()

        disk_warning = disk_percent > warn_disk_free
        disk_critical = disk_percent > crit_disk_free
        cache_warning = cache_free < warn_filecache
        cache_critical = cache_free < crit_filecache
        swap_warning = swap_free < warn_swap
        swap_critical = swap_free < crit_swap


def sendmail():
    """ invoke sendmail and dispatch """
    warn = Data.disk_warning or Data.cache_warning or Data.swap_warning
    crit = Data.disk_critical or Data.cache_critical or Data.swap_critical

    if warn or crit:
        message = "Resource report for %s on %s\n\n" % (Data.servername, time.ctime())
        subject = ""
        if crit:
            subject = "CRITICALLY low resources on %s" % Data.servername
        elif warn:
            subject = "WARNING! Low resources on %s"    % Data.servername
        else:
            subject = "Resources OK on %s" % Data.servername

        if Data.disk_critical:
            message += "Disk space critically low, using %2.2f %s\n" % (Data.disk_percent, "%")
        elif Data.disk_warning:
            message += "WARN: Disk space running low, using %2.2f %s\n" % (Data.disk_percent, "%")
        else:
            message += "Disk space is sufficient %d KB free\n" % (Data.disk_free)

        if Data.cache_critical:
            message += "File cache filling up, only %d KB are free\n" % Data.cache_free
        elif Data.cache_warning:
            message += "File cache filling up, only %d KB are free\n" % Data.cache_free
        else:
            message += "File cache has %d KB free, sufficient for now!\n" % Data.cache_free

        if Data.swap_critical:
            message += "Swap running out, only %d KB are free\n" % Data.swap_free
        elif Data.swap_warning:
            message += "Swap running out, only %d KB are free\n" % Data.swap_free
        else:
            message += "Swap still has %d KB free, good enough!\n" % Data.swap_free

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = "me@inter.net"
        msg['To'] = "you@inter.net"
        _s = smtplib.SMTP(local_hostname="localhost")
        _s.connect()
        _s.sendmail("me@inter.net", ["you@inter.net"], msg.as_string())
        _s.quit()


if __name__ == "__main__":
    d_tot, d_used, d_free, d_perc = diskfree()
    print("Total speace on partition is: %d KB" % Data.disk_total)
    print("Used space on partiion is: %d KB" % Data.disk_used)
    print("Free space on partition is: %d KB" % Data.disk_free)
    print("Percentage used is: %2.5f %s" % (Data.disk_percent, "%"))

    m_tot, m_used, m_free, c_used, c_free, s_tot, s_used, s_free = freespace()
    print("Memory total is: %d KB" % Data.mem_total)
    print("Memory used  is: %d KB" % Data.mem_used)
    print("Memory free  is: %d KB" % Data.mem_free)

    print("Disk Cache used is: %d KB" % Data.cache_used)
    print("Disk Cache free is: %d KB" % Data.cache_free)

    print("Swap total is: %d KB" % Data.swap_total)
    print("Swap used is: %d KB" % Data.swap_used)
    print("Swap free is: %d KB" % Data.swap_free)

    if Data.disk_critical:
        print("sending critically low diskspace message %d > %d" % (Data.disk_percent, Data.crit_disk_free))
    elif Data.disk_warning:
        print("sending warning low diskspace message %d > %d" % (Data.disk_percent, Data.warn_disk_free))

    if Data.cache_critical:
        print("sending criticaly low filecache message %d < %d" % (Data.cache_free, Data.crit_filecache))
    elif Data.cache_warning:
        print("sending warning low filecache message %d < %d" % (Data.cache_free, Data.warn_filecache))

    if Data.swap_critical:
        print("sending critically low swap message %d < %d" % (Data.swap_free, Data.crit_swap))
    elif Data.swap_warning:
        print("sending warning low swap message %d < %d" % (Data.swap_free, Data.warn_swap))
    sendmail()
