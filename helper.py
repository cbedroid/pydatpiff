import re

class String():
  @classmethod
  def lower(cls,string):
    ''' return lowered and strip string'''
    return string.lower().strip()

  @classmethod
  def title(cls,string):
    return string.lower().strip().title()

  @classmethod
  def filter(cls,string,pattern,pattern_two):
    return re.sub(pattern,pattern_two,string)





  
