<img src="https://user-images.githubusercontent.com/54720725/96840060-f872ab80-1417-11eb-93ac-c964217b98b1.png" width="100%" height="300">

[![PyPI](https://img.shields.io/pypi/v/pydatpiff.svg?color=blue)](https://pypi.python.org/pypi/pydatpiff) ![Build](https://api.travis-ci.org/cbedroid/pydatpiff.svg?branch=master)

# Introduction

**PyDatpiff** - <img class="emoji" alt="notes" height="20" width="20" src="https://github.githubassets.com/images/icons/emoji/unicode/1f3b6.png">
Unofficial [Datpiff](https://www.datpiff.com) Music Application. Play and download the latest Hip-Hop and RnB songs.

- Supports Windows, Mac, and Linux
- Python 3.3 - above

[**Documentation**](https://cbedroid.github.io/pydatpiff/) is still undergoing, but you can still visit it here.

**Full documentation** will be available soon!

# Dependencies

**PyDatpiff requires:**

- see requirements: [requirements.txt](https://github.com/cbedroid/pydatpiff/blob/master/requirements.txt)
- _python >= 3.3_

# Installation

The default media player uses VLC to play music.
For systems that are incompatible with VLC, MPV will be used as the fallback player.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; _click link to download_

[VLC](https://www.videolan.org/vlc/index.html) - VideoLan Client media player and framework.

[MPV](https://mpv.io/installation/) - MPV Framework. ( Supports IOS, Android and Linux Systems )

For linux based systems, &nbsp; use `apt-get` to install required repos

### VLC

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

# Quick Start

## Mixtapes

**Import PyDatpiff module and Intialize Mixtapes class**
There are two parameters that can be pass to Mixtapes Instance.

Only one parameter should be called at a time. If no parameter is pass, **"category"** will be set to **"hot"** by default.

- **params:** `category` and `search`:

  - **_category_** :

    - _'hot' , 'new', 'top',celebrated', 'popular', 'exclusive', 'most download', ' most listen', 'most favorite',' highest rating'_

    - **_search_**:

      - artist name or artist mixtape name.

  - **_limit_**:

    - maximum amount of mixtapes to return. default=600

---

| Category             | Description                                  |
| -------------------- | -------------------------------------------- |
| **"hot"**            | Mixtapes that are hot for the week.          |
| **"new"**            | Mixtapes that are brand-new or just release. |
| **"top"**            | Mixtapes that are top-ranking.               |
| **"celebrated"**     | Top ranking celebrity mixtapes.              |
| **"popular"**        | Popular mixtapes available.                  |
| **"exclusive"**      | Exclusive mixtapes.                          |
| **"most download"**  | Most downloaded mixtapes.                    |
| **"most listen"**    | Most listen mixtapes.                        |
| **"most favorite"**  | Favorite mixtapes.                           |
| **"highest rating"** | Mixtapes with the highest rating.            |

---

# Let's Get Started

_Create an Instance of the Mixtapes class_

```python
import pydatpiff
>>> mix = pydatpiff.Mixtapes(category='hot')
#OR
#Search for an artist's mixtape
>>> mix = pydatpiff.Mixtapes(search='Jay-Z')

# To view all available mixtapes
>>> mix.mixtapes
```

['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z : 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard C lassics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1', 'Jay-z - Remixes',..etc ]

# Media

### Now Lets create a Media object to play some songs

**pydatpiff.Media** - is a class that controls the PyDatpiff Media Player.

_HERE ARE SOMETHINGS YOU CAN DO:_

- `findSong` - Find any song made by an artist.
- `play` - Plays songs from current album.
- `download` - Download current song.
- `downloadAlbum` - Download all songs from an album.

### Setup media player with an album

Setting media player with an album from above.

> `Albums`**:** _['Creative Control', 'Carter Collection (15th Anniversary)', ..etc]_

Mixtape's ablum can be reference either by `index` or by its `album name`.
Index starts at **one (1)** not **~~zero (0)~~** .

```python

#We pass in the "mix" object from Mixtapes class
>>> media = pydatpiff.Media(mix)

#Set the media player to an ablum.
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

---

&nbsp; &nbsp; &nbsp; <a><img src="https://github.com/cbedroid/pydatpiff/blob/master/github/gif/gif_mixtapes.gif " align=center width=550 height=400/></a>

## PLAY A SONG

> Songs can be played either by referencing the song **index** or **name**.
> Song's name **do not** have to be an exact match.

```python
>>> media.play('Welcome')

#OR

>>> media.play(3)
```

---

### Play Song - &#9836;&#9836;&#9836;

Artist: Jay-Z

Song: Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street

Size: 1.91 MB

---

&nbsp; &nbsp; &nbsp; <a><img src ="https://github.com/cbedroid/pydatpiff/blob/master/github/gif/gif_media.gif " align=center width=550 height=400/></a>

# Find A Song

<img src="https://raw.github.com/cbedroid/pydatpiff/master/github/EmojiThinking.png" width="100" height="100"> **. . . CANT FIND A SONG ??**

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

---

## CONTROLLING MEDIA PLAYER

Media player _can `rewind` , `fast-forward` , `pause` , `stop` and control `volume`_ of song.

```python
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

  - **params**: `song` , `output`, and `rename`

    - _**song**_ : index or name of song.

    - _**output**_ : directory to save song. \*(default: current directory)

    - _**rename**_ : rename song. _(optional)_

> ## Download Album

- **media.downloadAlbum** - **params**: `output` - _**output**_ : directory to save song. _(default: current directory)_

```python
#Download a single song
>>> media.download(3,output="directory_to_save_song")
#OR
>>> media.download('Welcome',output="directory_to_save_song")


#Download full album
>>> media.downloadAlbum(output='directory_to_save_album')
```

---

## LINKS

- [Code](https://github.com/cbedroid/pydatpiff)
- [PyPI](https://pypi.org/project/pydatpiff/)
- [Issues & Bugs](https://github.com/cbedroid/pydatpiff/issues)
