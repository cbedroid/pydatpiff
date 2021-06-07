 [![PyPI](https://img.shields.io/pypi/v/pydatpiff.svg?color=blue)](https://pypi.python.org/pypi/pydatpiff)  ![Build](https://api.travis-ci.org/cbedroid/pydatpiff.svg?branch=master)

<img src="https://user-images.githubusercontent.com/54720725/96840060-f872ab80-1417-11eb-93ac-c964217b98b1.png" width="800" height="200">

# Pydatpiff

**PyDatpiff**   -   🎶 Unofficial [Datpiff](https://www.datpiff.com) Music Application. Play and download the latest Hip-Hop and RnB songs.
  - supports windows, mac, and linux
  - python 3.6 - above

## Dependencies

**PyDatpiff requires:**
 - see requirements:  [requirements.txt](https://github.com/cbedroid/pydatpiff/blob/master/requirements.txt)
- *python >= 3.6*

## Installation

 The default media player uses VLC to play music.
 For systems that are incompatible with VLC,  MPV will be used as the fallback player.


[**VLC**](https://www.videolan.org/vlc/index.html) - VideoLan Client media player and framework.

[**MPV**](https://mpv.io/installation/) -  MPV Framework. ( Supports IOS, Android and Linux Systems )
--- --- 
For linux based systems,  &nbsp; use `apt-get` to  install required repos

#### VLC
```bash
sudo apt-get install vlc
```
#### MPV
```bash
sudo apt-get install mpv
```

#### Install Pydatpiff Module
```bash
pip3 install pydatpiff
```
--- ---




#### Pydatpiff Category & Description

Category reference a mixtapes level or ratings. Visit [**Datapiff**](https://datpiff.com) for more info.

---
 | Category                           |      Description                           |
|-------------------------------------|--------------------------------------------|
|[__hot__][hot]                       | Mixtapes that are hot for the week.
|[__new__][new]                       | Mixtapes that are brand-new or just release.
|[__top__][top]                       | Mixtapes that are top-ranking.
|[__celebrated__][celebrated]         | Top ranking celebrity mixtapes.
|[__popular__][popular]               | Popular mixtapes  available.
|[__exclusive__][exclusive]           | Exclusive mixtapes.
|[__most download__][most-download]   | Most downloaded mixtapes.
|[__most listen__][most-listen]       | Most listen mixtapes.
|[__most favorite__][most-favorite]   | Favorite mixtapes.
|[__highest rating__][highest-rating] | Mixtapes with the highest rating.

--- ---


## Mixtapes

**pydatpiff.Mixtapes** - PyDatpiff Mixtapes class is query for the latest music by either referencing a `category` or by searching for a particular `artist` or `mixtape`.

 __Import PyDatpiff module and Intialize Mixtapes class__

Mixtapes can accept up to three arguments:  __category__ , __search__ and __limit__.

Either argument __category__ or __search__ should be used at a given time. If no arguments are pass,  **"category"** will be set to   __"hot"__ by default.

- **params:**  __category__ ,  __search__, __limit__:
	 - __*category*__ :

        - *'hot' , 'new', 'top',celebrated', 'popular', 'exclusive', 'most download', ' most listen', 'most favorite',' highest rating'*

     - __*search*__:

        - artist name or artist mixtape name.

    - __*limit*__:

        - maximum amount of mixtapes to return. default=600



*Create an Instance of the Mixtapes class*
```python
>>> from pydatpiff.mixtapes import Mixtapes

>>> mix = Mixtapes(category='hot')
#OR
#Search for an artist's mixtape
>>> mix = Mixtapes(search='Jay-Z')

# To view all available mixtapes
>>> mix.mixtapes
```

['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z                                                                                                : 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard C                                                                                                lassics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big                                                                                                 Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z                                                                                                 & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1',                                                                                                 'Jay-z - Remixes',..etc ]

--- ---

## Media

**pydatpiff.Media** - PyDatpiff class that allow users to play and download songs


Here are somethings you can do with **`Pydtapiff Media`**
 - `findSong` - Find any song made by an artist.
 - `play`  - Plays songs from  current mixtape.
 - `download` - Download current song.
 - `downloadAlbum` - Download all songs from an mixtape.

--- ---
 #### Setup and play song from a mixtape
 Setting media player with a mixtape from above.
>`Mixtape`__:__ *['Creative Control', 'Carter Collection (15th Anniversary)', ..etc]*

 Mixtape can be reference either by __index__  or by its __album name__.
  Index starts at __one (1)__  not __~~zero (0)~~__ .

```python

#We initialized Media with a mixtape object from Mixtapes class
>> from pydatpiff.media import Media
>>> media = Media(mix)

#Setup the media player to a particular mixtapes.
>>> media.setMedia('Creative Control')
#OR
>>> media.setMedia(1) # set media by index.  1='Creative Control'

#TO VIEW ALL AVAILABLE SONGS
>>> media.songs

[ 'Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)',
  'Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street'                                                                                         , "Jay-Z - Jay's Back ASAP",
  'Jay-Z - Live In London',
  'Jay-Z - Green Magic',
  'Jay-Z - Brooklyn Sound Boy',
  'Jay-Z - Child Abuse (Prod. By Green Lantern)',
  'Jay-Z - Jay-Z Speaks On Green Lantern',
  'Jay-Z - Flashy Life',
  'Jay-Z - Got Me On My Shit (Prod. By Green Lantern)',
  ..etc
 ]
```

--- ---

&nbsp; &nbsp; &nbsp; <a>
<img src="https://i.ibb.co/dPVhwXr/gif-mixtapes.gif" alt="gif-mixtapes" border="0" align="center" min-width="300px" width="80%" height="100%"/>
</a>

--- ---

### PLAYING A SONG
Songs can be played either by referencing the song  **index** or   **name**.

Song's name __do not__ have to be an exact match.


```python
>>> media.play('Welcome')

#OR

>>> media.play(3)
```


 #### Play Song -  &#9836;&#9836;&#9836;
  Artist: Jay-Z

  Song: Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street

  Size:  1.91 MB


&nbsp; &nbsp; &nbsp; <a>
<img src="https://i.ibb.co/mX1x250/gif-media.gif" alt="gif-media" border="0" align="center" min-width="300px" width="80%" height="100%"/>
</a>
--- ---

### FIND A SONG

<img src="https://user-images.githubusercontent.com/54720725/97070237-dbb7ae80-15a4-11eb-9ab1-c27b0a2a64dc.png" width="100" height="100">

**. . . Can't find that song you been looking for??**

  **No worries... We got you covered!**

Find any song made by an artist using the **`findSong`** method in **`media`**.

  - search by `song's name`.
  - search by `album's name`.

 **media.findSong**
```python
   #Search for a song
   >>> media.findSong('green lan') # returns mixtape's index and name

   #results
   [(1, 'Creative Control'),
    (36, 'Headliner & Legends (Jay-Z Freestyles) '),
    (69, 'Power Us Up( Jay-z, Kanye West, Swizz Beatz)'),
    (172, 'J3 Rocnation '),(254, "Bakin' Session")
   ]
```
--- ---

 ### CONTROLLING MEDIA PLAYER
 Media player *can    `rewind` , `fast-forward` , `pause` ,  `stop` and control `volume`* of song.


 Using **`media.player`**, you will have complete control over your music player.

Simply create a variable ` player = media.player`

 - `info` -  get information about a song
 - `name` -  get name of current song.
 - `duration` - get duration of track.
 - `rewind` - rewind track
 - `ffwd` - fast-forward track
 - `play` - play current *( track must be paused or stop )*.
 - `pause` - pause/unpause track.
 - `stop` - stop track.
 - `volume` - set the volume level (1 - 100).
 - `volumeUp` - increase volume ( *default: increase by 5*).
 - `volumeDown` - decrease volume ( *default: decrease by 5*).


``` python
 # create an object of the player class
 >>> player = media.player

 # Rewind ⏪

>>> player.rewind()
>>> player.rewind(10) # rewind 10 sec ago

# Fast-Forward ⏩
>>> player.ffwd()
>>> player.ffwd(10) # fast-forward 10 sec ahead

# Pause ⏸
>>> player.pause

# Stop ⏹
>>> player.stop # stop song

# Volume 🔊
>>> player.volume(50) # set media volume to 50
>>> player.volumeDown(5) # set media volume down 5 steps
>>> player.volumeUp(5) # set media volume up 5 steps

```

 ## DOWNLOAD SONGS AND ALBUMS
> ## Download Song

  - **media.download**
	   - __params__: `song` , `output`, and `rename`

            - *__song__* : index or name of song.

	        - *__output__* : directory to save song. *(default: current directory)

            - *__rename__* : rename song. *(optional)*



 > ## Download Album

  -	 **media.downloadAlbum**
        - __params__: `output`

            - *__output__* : directory to save song. *(default: current directory)*


```python
#Download a single song
>>> media.download(3,output="directory_to_save_song")
#OR
>>> media.download('Welcome',output="directory_to_save_song")


#Download full album
>>> media.downloadAlbum(output='directory_to_save_album')
```

--- ---
## LINKS
- [Code](https://github.com/cbedroid/pydatpiff)
- [PyPI](https://pypi.org/project/pydatpiff/)
- [Issues & Bugs](https://github.com/cbedroid/pydatpiff/issues)

[new]: https://www.datpiff.com/mixtapes
[hot]: https://www.datpiff.com/mixtapes/hot
[top]: https://www.datpiff.com/mixtapes-hot.php
[celebrated]: https://www.datpiff.com/mixtapes/celebrated
[exclusive]: https://www.datpiff.com/mixtapes-exclusive
[popular]: https://www.datpiff.com/mixtapes-popular.php
[highest-rating]: https://www.datpiff.com/mixtapes-popular.php?filter=month&sort=rating
[most-listen]: https://www.datpiff.com/mixtapes-popular.php?filter=month&sort=listens
[most-download]: https://www.datpiff.com/mixtapes-popular.php?filter=month&sort=downloads
[most-favorite]: https://www.datpiff.com/mixtapes-popular.php?filter=month&sort=favorites



