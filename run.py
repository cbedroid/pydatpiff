from src.mixtapes import Mixtapes
from src.media import Media

mix = Mixtapes(search='Lil Boosie')
media = Media(mix)
media.setMedia(1)
media.play(6)

input('>>')
