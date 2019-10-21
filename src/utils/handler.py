import platform 
import math
import subprocess


def fixdate():
    date = None
    _f = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if platform.system() == "Linux":
        try:
            _f = 'date +"%m/%d/%y  %I:%M:%S %p"'
            date = subprocess.check_output(_f).decode('utf-8').strip()
            date += ' %(name)s - %(levelname)s - %(message)s'
        except:
            pass
    else:
        date = _f
    return date



def converter(file_size):
    """Convert file size and returns user readable size""" 
    if file_size == 0:
        return '0B'
    
    size_name = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    change = int(math.floor(math.log(file_size,1024)))
    power = math.pow(1024,change)
    result = round(file_size / power,2)
    return '%s %s'%(result,size_name[change])
 
