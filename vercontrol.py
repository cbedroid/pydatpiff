# Control the version numbering for git repo

import re
from subprocess import check_output

def getVersion():
    try:
        version_re_format = "(v\d\.\d\.\d)"
        version = check_output('git tag',shell=True).decode('utf8').strip()
        if version:
            version = version.split('\n')[-1]
        return re.match(version_re_format,version)[0]
    except:
        emsg = ("Version Control Failed!"
            "\n\n---> Version Control - Package must contain a Release Version."
            "\n---> For more help visit - https://git-scm.com/book/en/v2/Git-Basics-Tagging")
        print(esmg)
    return "1.1.0" 



print(getVersion())
