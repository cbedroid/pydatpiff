from .mixtapes import Mixtapes
from .media import Media 
from .Request import Session

class Datpiff(Media,Mixtapes):
    def __init__(self,*args,**kwargs):
        super(Datpiff,self).__init__(*args,**kwargs)


if __name__ == '__main__':
    dp = Datpiff()
