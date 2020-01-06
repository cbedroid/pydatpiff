
<img src="https://raw.github.com/cbedroid/pydatpiff/dev2/github/Logo.png" width="800" height="200">

[![PyPI](https://img.shields.io/pypi/v/pydatpiff.svg?color=blue)](https://pypi.python.org/pypi/pydatpiff)  ![Build](https://api.travis-ci.org/cbedroid/pydatpiff.svg?branch=master)
# Introduction

**PyDatpiff**   -  Unofficial Datpiff python program that interact with online [Datpiff](https://www.datpiff.com) Mixtapes. PyDatpiff allow users to play and download songs from thier favorite music artist.

  - supports windows, mac, and linux
  - python 3.3 - above

## Dependencies

**PyDatpiff requires:**
 - see requirements:  [requirements.txt](https://github.com/cbedroid/pydatpiff/blob/master/requirements.txt)
- *python>= 3.3*
- [VLC](https://www.videolan.org/vlc/index.html)- VideoLan Client media player and framework
# Installation
Install [VLC](https://www.videolan.org/vlc/index.html)  *(if not already install)*

```bash
pip install pydatpiff
```

# Quick Start
 ##  Mixtapes
 __Import PyDatpiff module and Intialize Mixtapes class__
	
There are two parameters that can be pass to Mixtapes Instance.

*Only one parameter should be called at a time. If no parameter is pass, category      will    be set the __"hot"__.*
- **params:** `category` and `search`:
	 - __*category*__ :
	    
        - *'hot' , 'new', 'top',celebrated', 'popular', 'exclusive', 'most download', ' most listen', 'most favorite',' highest rating'*
	  
     - __*search*__:
		
        - artist name or artist mixtape name.




---
 | Category                |               Description     |
|-------------------|-------------------|
|__"hot"__                      | Mixtapes that are hot for the week.
|__"new"__                      | Mixtapes that are brand-new or just release.
|__"top"__                      | Mixtapes that are top-ranking.
|__"celebrated"__       | Top ranking celebrity mixtapes.
|__"popular"__          | Popular mixtapes  available.
|__"exclusive"__        | Exclusive mixtapes.
|__"most download"__| Most downloaded mixtapes.
|__"most listen"__      | Most listen mixtapes.
|__"most favorite"__| Favorite mixtapes.
|__"highest rating"__| Mixtapes with the highest rating.
---
# Let's Get Started...
*Create an Instance of the Mixtapes class*
```python
import pydatpiff
>>> mix = pydatpiff.Mixtapes(category='hot')

#OR

#Search for an artist's mixtape
>>> mix = pydatpiff.Mixtapes(search='Jay-Z')

# To view all available mixtapes
>>> mix.mixtapes
```

['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z                                                                                                : 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard C                                                                                                lassics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big                                                                                                 Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z                                                                                                 & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1',                                                                                                 'Jay-z - Remixes',..etc ]


# Media
### Now Lets create a Media object to play  some songs !!

**pydatpiff.Media** -  is a class that controls the PyDatpiff Media Player.

 _THINGS YOU CAN DO:_
 - `findSong` - find any song made by an artist
 - `play`  - plays songs from album
 - `download` - download song
 - `downloadAlbum` - download all songs from album

 ### Setup media player with an album
 Setting media player with an album from above.
>`Albums`__:__ *['Creative Control', 'Carter Collection (15th Anniversary)', ..etc]*

 Mixtape's ablum can be reference either by `index`  or by its  `album name`.
  Index starts at __one (1)__  not __~~zero (0)~~__ .

```python

#We pass in the 'mix' object from Mixtapes class
>>> media = pydatpiff.Media(mix)

#Set the media to an ablum.
>>> media.setMedia('Creative Control')
#Or
>>> media.setMedia(1) # set media by index.  1='Creative Control'

#TO VIEW ALL AVAILABLE SONGS
>>> media.songs
```
 [ 'Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)', 'Jay-Z - Welcome 2 Atla                                                                                                nta V103 Feat. Young Jeezy & DJ Greg Street', "Jay-Z - Jay's Back ASAP", 'Jay-Z - Live In London                                                                                                ', 'Jay-Z - Green Magic', 'Jay-Z - Brooklyn Sound Boy', 'Jay-Z - Child Abuse (Prod. By Green Lan                                                                                                tern)', 'Jay-Z - Jay-Z Speaks On Green Lantern', 'Jay-Z - Flashy Life', 'Jay-Z - Got Me On My Sh                                                                                                it (Prod. By Green Lantern)',..etc ]

--- --
# Find A Song 
<img src="https://raw.github.com/cbedroid/pydatpiff/dev2/github/EmojiThinking.png" width="100" height="100"> **. . . CANT FIND A SONG??**
```python
   #Search for a song
   >>> media.findSong('green lan') # returns mixtape's index and name
```

[(1, 'Creative Control'), (36, 'Headliner & Legends (Jay-Z Freestyles) '), (69, 'Power Us Up( Jay-z, Kanye West, Swizz Beatz)'), (172, 'J3 Rocnation '), (254, "Bakin' Session")]

--- ---
# Lets Play Some Songs !!
### PLAYING SONG
Songs can be played either by referencing the song  **index** or   **name**.

Song's name __do not__ have to be an exact match.


```python
>>> media.play('Welcome')

#OR

>>> media.play(2)

```

 ### CONTROLLING MEDIA PLAYER
 Media player *can   `rewind` , `fast-forward` , `pause` ,  `stop` and control `volume`*.

``` python
 # create an object of the player class
 >>> player = media.player

 # Rewind
>>> player.rewind()
>>> player.rewind(10) # rewind 10 sec ago

# Fast-Forward
>>> player.ffwd()
>>> player.ffwd(10) # fast-forward 10 sec ahead

# Pause
>>> player.pause

# Stop
>>> player.stop # stop song

# Volume
>>> player.volume(50) # set media volume to 50
>>> player.volumeDown(5) # set media volume down 5 steps
>>> player.volumeUp(5) # set media volume up 5 steps

```

  ### DOWNLOAD SONG AND ALBUM
  - **Download Song**
	  
	   - __params__: `song` , `output`, and `rename`
		    
            - *__song__* : index or name of song.

	        - *__output__* : directory to save song. *(default: current directory)

            - *__rename__* : rename song. *(optional)*

-    **Download Album**
        - __params__: `output`
          
            - *__output__* : directory to save song. *(default: current directory)*


```python
#Download a single song
>>> media.download(1,output="directory_to_save_song")
#OR
>>> media.download('Welcome',output="directory_to_save_song")


#Download whole album
>>> media.downloadAlbum(output='directory_to_save_album')
```
--- ---
## LINKS
- [Code](https://github.com/cbedroid/pydatpiff)
- [PyPI](https://pypi.org/project/pydatpiff/)
- [Issues & Bugs](https://github.com/cbedroid/pydatpiff/issues)


