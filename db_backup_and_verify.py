#!/usr/bin/env python

""" dump (mysql)db, transfer and md5 verify on remote server """

from email.mime.text import MIMEText
import time
import os
import sys
import gzip
import traceback
import smtplib
import subprocess as sp
import paramiko


class Messages:
    dout = ""
    derr = ""
    dsuc = False
    dstart = ""
    dend = ""
    dferr = None
    dfout = None
    pout = ""
    perr = ""
    psuc = False
    pstart = ""
    pend = ""
    rerr = None
    rout = None
    sout = ""
    serr = ""
    ssuc = False
    sstart = ""
    send = ""


def dumpdb(folder, filename):
    """ test """
    try:
        print("Dumping database to file %s" % filename)
        fout = open(folder+filename, 'w')
        ret = sp.call(("mysqldump", "--all-databases", "--single-transaction", "--quick"), stdout=fout)
        fout.close()
        if ret == 0:
            print("Dumped database successfully")
            Messages.dout += "Successfully dumped database to %s\n" % (folder+filename)
            Messages.dsuc = True
            return True
        else:
            print("Failed to dump database, errorcode = %d" % ret)
            Messages.derr += "Failed to dump database, errorcode = %d\n" % ret
            return False
        return ret
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lst = traceback.format_list(traceback.extract_tb(exc_traceback))
        for _s in lst:
            Messages.derr += _s
        return False


def pack(folder, filename):
    """ ziploc """
    try:
        print("Compressing %s") % (folder+filename)
        fin = open(folder+filename, 'r')
        gzout = gzip.open(folder+filename+".gz", 'wb')
        for line in fin:
            gzout.write(line)
        gzout.close()
        fin.close()
        print("Successfully compressed %s") % (folder+filename+".gz")
        Messages.pout += "Successfully compressed %s\n" % (folder+filename+".gz")
        print("Removing %s") % (folder+filename)
        os.remove(folder+filename)
        Messages.psuc = True
        return True
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lst = traceback.format_list(traceback.extract_tb(exc_traceback))
        for _s in lst:
            Messages.perr += _s
        print("Failed to compress %s. \nRemoving files") % (folder+filename)
        Messages.perr += "\nFailed to compress %s. \nRemoving files\n" % (folder+filename)
        os.remove(folder+filename)
        os.remove(folder+filename+".gz")
        return False


def send_and_check(local_dir, filename, user, server, remote_dir, ssh_key):
    try:
        print("Logging into backup at: %s") % server
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(hostname=server, username=user, key_filename=ssh_key)
        sftp = client.open_sftp()
        print("Verifying dump file on: %s") % server
        r_stat = sftp.lstat(remote_dir+filename)
        l_stat = os.stat(local_dir+filename)
        print("Computing md5sum for remote dumpfile")
        rout, rerr = client.exec_command(("md5sum %s" % (remote_dir+filename)))
        print("Computing md5sum for local dumpfile")
        tmp = sp.Popen(["md5sum", local_dir+filename], stdout=sp.PIPE)
        tmp.wait()
        lout, lerr = tmp.communicate()
        rmd5 = rout.read().split(" ", 1)
        lmd5 = lout.split(" ", 1)
        if r_stat.st_size == l_stat.st_size and rmd5 == lmd5:
            print("Both stats report the same size and md5sum")
            Messages.sout += "Successfully sent %s to %s\n" % (filename, server)
            print("Remote size = %d") % r_stat.st_size
            Messages.sout += "Remote size = %d\n" % r_stat.st_size
            print("Local size = %d") % l_stat.st_size
            Messages.sout += "Local  size = %d\n" % l_stat.st_size
            print("Remote MD5 = %s") % rmd5
            Messages.sout += "Remote MD5  = %s\n" % rmd5
            print("Local MD5 = %s") % lmd5
            Messages.sout += "Local MD5 = %s\n" % lmd5
            Messages.ssuc = True
            return True
        else:
            print("The two stats report different sizes or the md5sums differ")
            Messages.sout += "Failed to send %s to %s\n" % (filename, server)
            print("Remote size = %d") % r_stat.st_size
            Messages.sout += "Remote size = %d\n" % r_stat.st_size
            print("Local size = %d") % l_stat.st_size
            Messages.sout += "Local size = %d\n" % l_stat.st_size
            print("Remote MD5 = %s") % rmd5
            Messages.sout += "Remote MD5 = %s\n" % rmd5
            print("Local MD5 = %s") % lmd5
            Messages.sout += "Local MD5 = %s\n" % lmd5
            return False
    except Exception:
        print("Exception raised while sending %s to %s") % (filename, server)
        Messages.serr += "Exception raised while sending %s to %s\n" % (filename, server)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lst = traceback.format_list(traceback.extract_tb(exc_traceback))
        for s in lst:
            Messages.serr += s
        return False


def remote_execute(dir, filename, param, server, user, ssh_key):
    try:
        print("Executing %s on %s") % ("["+dir+filename+" "+param+"]", "["+server+"]")
        Messages.rout += "Executing %s on %s\n" % ("["+dir+filename+" "+param+"]", "["+server+"]")
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(hostname=server, username=user, key_filename=ssh_key)
        rin, rout, rerr = client.exec_command(dir+filename+" "+param)
        print("Output from execution:")
        Messages.rout += "Output from execution:\n"
        out = rout.readline()
        while out:
            print(out)
            Messages.rout += out
            out = rout.readline()
        err = rerr.read()
        if not err:
            print("Succsessfully executed %s on %s") % ("["+dir+filename+" "+param+"]", "["+server+"]")
            Messages.rout += "Succsessfully executed %s on %s\n" % ("["+dir+filename+" "+param+"]", "["+server+"]")
            Messages.rsuc = True
            return True
        else:
            Messages.rout += "Faled to execute %s on %s\n" % ("["+dir+filename+" "+param+"]", "["+server+"]")
            print("Got an error while executing:\n%s") % err
            Messages.rerr += "%s\n" % err
            return False
    except Exception:
        print("Script case local error")
        Messages.rout += "Exception raised while executing %s on %s\n" % (filename, server)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lst = traceback.format_list(traceback.extract_tb(exc_traceback))
        for s in lst:
            Messages.rerr += s
        return False


def disc_free(user, server, ssh_key):
    """ enough disk? """
    try:
        Messages.dfout += "Disc free on %s after backup:\n" % server
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(hostname=server, username=user, key_filename=ssh_key)
        cmd = "df -h"
        rin, rout, rerr = client.exec_command(cmd)
        Messages.dfout += rout.read()
        Messages.dferr += rerr.read()
        print(Messages.dfout)
        print(Messages.dferr)
        Messages.dfsuc = True
        return True
    except Exception:
        print(cmd + "caused local error")
        Messages.dfout += "Exception raised while executing" + cmd + "on %s\n" % (server)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lst = traceback.format_list(traceback.extract_tb(exc_traceback))
        for _s in lst:
            Messages.dferr += _s
        return False


def send_mail(sender, receiver):
    """ send mail! """
    subject = ""
    if Messages.ssuc and Messages.psuc and Messages.dsuc:
        subject = "Database backup chain SUCCESS %s" % time.ctime()
    else:
        subject = "Database backup chain FAILED %s" % time.ctime()

    message = ""
    if Messages.dsuc:
        message += "DUMP SUCCESS:\n%s" % Messages.dout
        message += "Start time = %s\n" % Messages.dstart
        message += "End time = %s\n" % Messages.dend
    else:
        message += "DUMP FAILED:\n%s" % Messages.dout
        message += "DUMP ERRORS:\n%s" % Messages.derr
        message += "Start time = %s\n" % Messages.dstart
        message += "End time = %s\n" % Messages.dend
    message += "\n\n"
    # if Messages.pstart and Messages.pend:
    if Messages.psuc:
        message += "PACKAGING SUCCESS:\n%s" % Messages.pout
        message += "Start time = %s\n" % Messages.pstart
        message += "End time = %s\n" % Messages.pend
    else:
        message += "PACKAGING FAILED:\n%s" % Messages.pout
        message += "PACKAGING ERRORS:\n%s" % Messages.perr
        message += "Start time = %s\n" % Messages.pstart
        message += "End time = %s\n" % Messages.pend
    message += "\n\n"
    # if Messages.sstart and Messages.send:
    if Messages.ssuc:
        message += "SEND SUCCESS:\n%s" % Messages.sout
        message += "Start time = %s\n" % Messages.sstart
        message += "End time = %s\n" % Messages.send
    else:
        message += "SEND FAILED:\n%s" % Messages.sout
        message += "SEND ERRORS:\n%s" % Messages.serr
        message += "Start time = %s\n" % Messages.sstart
        message += "End time = %s\n" % Messages.send
    message += "\n\n"
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(receiver)
    _s = smtplib.SMTP()
    _s.connect()
    _s.sendmail(sender, receiver, msg.as_string())
    _s.quit()


def run_verification():
    """ run verification! """

    print("Running database verification script")
    tmp = sp.Popen(["php", "/data/backup/verify_database_backup.php"], stdout=sp.PIPE)
    tmp.wait()
    lout, lerr = tmp.communicate()
    if not lerr:
        print("Database verification output:\n%s") % lout
        return True
    else:
        print("Database verification output:\n%s") % lout
        print("Database verification encountered an error:\n%s") % lerr
        return False


if __name__ == "__main__":
    _t = time.localtime()
    backup = "database.backup"
    sandbox = "database.sandbox"
    live_dir = "/data/backup/"
    backup_dir = "/mnt/backup/"
    sandbox_dir = "/root/"
    filename = "db_%04d%02d%02d%02d%02d.sql" % (_t.tm_year, _t.tm_mon, _t.tm_mday, _t.tm_hour, _t.tm_min)
    sender = "noreply@me.com"
    receiver = ["notification@me.com"]

    Messages.dstart = time.ctime()
    res = dumpdb(live_dir, filename)
    Messages.dend = time.ctime()
    if not res:
        send_mail(sender, receiver)
        sys.exit(1)

    Messages.pstart = time.ctime()
    res = pack(live_dir, filename)
    Messages.pend = time.ctime()
    if not res:
        send_mail(sender, receiver)
        sys.exit(2)

    filename += ".gz"

    Messages.sstart = time.ctime()
    res = send_and_check(live_dir, filename, "backup", backup,
                         backup_dir, "/data/backup/backup_private_key")
    Messages.send = time.ctime()
    if not res:
        send_mail(sender, receiver)
        os.remove(live_dir+filename)
        sys.exit(3)

    send_mail(sender, receiver)
    os.remove(live_dir+filename)
