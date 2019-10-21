import re 

class Parse():

    @classmethod 
    def toLink(text):
        return  re.findall(
                r'meta\scontent\="(//[\w/?].*)"\sitemprop', text)

    @classmethod 
    def toM4():
        self._m4link = re.search(
                        '/mixtapes/([\w\/]*)', text).group(1)
   



