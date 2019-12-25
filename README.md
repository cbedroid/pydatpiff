<<<<<<< HEAD
=======

<img src="https://i-love-png.com/images/c7ce1da7ed7ace50867927d6a6520e62.png" width="800" height                                                                                                ="200">
>>>>>>> 0d81f33... Added threading to mixsetup, Optimize speed of Mixtapes class

# DatPiff
![alt text](https://i-love-png.com/images/c7ce1da7ed7ace50867927d6a6520e62.png)

<<<<<<< HEAD
[![Build Status](https://travis-ci.org/cbedroid/Datpiff.svg?branch=master)](https://travis-ci.com/cbedroid/Datpiff)

# PyDatPiff
![alt text](https://i-love-png.com/images/c7ce1da7ed7ace50867927d6a6520e62.png)
<img src="https://i-love-png.com/images/c7ce1da7ed7ace50867927d6a6520e62.png" width="400" height="790">
=======
**PyDatpiff**   -  Unofficial Datpiff python program that interact with online [Datpiff](https://www.datpiff.com) Mixtapes. PyDatpiff allow users to play and download songs from thier favorite music artist.

  - supports windows, mac, and linux
  - python 3.3 - above
>>>>>>> 85ee64f... More refactoring

[![Build Status]('https://travis-ci.org/cbedroid/Datpiff.svg?branch=master')

<<<<<<< HEAD
# Introduction :
#### Datpiff - is a python program that interact with Datpiff Mixtapes 
  - supports windows,mac,and linux
  - python 3.4 - above 
   
### Dependencies:
- see requirements:  [requirements.txt](https://github.com/cbedroid/Datpiff/blob/master/requirements.txt) 
- __VLC__ - Datpiff requires the  installation of VLC 
=======
#### Dependencies:
see requirements:  [requirements.txt](https://github.com/cbedroid/Datpiff/blob/master/requirements.txt)
### Installation
=======
**PyDatpiff requires:**
 - see requirements:  [requirements.txt](https://github.com/cbedroid/pydatpiff/blob/master/requirements.txt)
- *python>= 3.3*
- [VLC](https://www.videolan.org/vlc/index.html)- VideoLan Client media player and framework
# Installation
Install [VLC](https://www.videolan.org/vlc/index.html)  *(if not already install)*
>>>>>>> 85ee64f... More refactoring

Datpiff requires:  **python3.4 - above** .
```bash
pip install Datpiff
```
# Quick Start
>##  Mixtapes
 __Import Datpiff module and Intialize Mixtapes class__
> **params:** `category` and `search`:
  
>>__*category*__ :
>>>*'hot' , 'new', 'top',celebrated', 'popular', 'exclusive', 'most 			
download', ' most listen', 'most favorite',' highest rating'*

>>__search__: 
>>>  *artist name or artist mixtape name*

|\|	Category		|		Description	\||
|-------------------|-------------------|
|__"hot"__			| Mixtapes that are hot for the week. 
|__"new"__			| Mixtapes that are brand-new or just release.
|__"top"__			| Mixtapes that top-ranking.
|__"celebrated"__	| Top ranking celebrity mixtapes.
|__"popular"__		| Popular mixtapes  available.   
|__"exclusive"__	| Exclusive mixtapes.
|__"most download"__| Most downloaded mixtapes.
|__"most listen"__	| Most listen mixtapes.
|__"most favorite"__| Favorite mixtapes. 
|__"highest rating"__| Mixtapes with the highest rating.
---
=======
## Quick Start
Import Datpiff module and Intialize Mixtapes class
**params:** `category` and `search`: 
`category` :
- "hot" 
- "new",
- "top",
- "celebrated",
- "popular",
- "exclusive",
- "most download",
- "most listen",
- "most favorite"
- "highest rating"

`search`: 
: artist name or artist mixtape name

```python 
import datpiff
mix = datpiff.Mixtapes(category='hot')

#OR

#search for an artist mixtapes
mix = datpiff.Mixtapes(search='Jay-Z')
```
# Media 
`datpiff.Media` -  is class that controls the Datpiff Media Player.
>#### THINGS YOU CAN DO: 
>> - `play`  - plays songs from album
>> - `download` - download song
>>- `downloadAlbum` - download all songs from mixtape album
=======

#### Now Initailize Media class

```python
import datpiff

mix = datpiff.Mixtapes(search='Jay-Z')
# we pass in Mixtapes' instance to the Media class
media = datpiff.Media(mix)


<<<<<<< HEAD
#### To view all available Mixtapes Ablums
>>> mix.mixtapes 
```
    ['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z: 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard Classics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1', 'Jay-z - Remixes',..etc ]
=======
 _THINGS YOU CAN DO:_
 - `findSong` - find any song made by an artist
 - `play`  - plays songs from album
 - `download` - download song
 - `downloadAlbum` - download all songs from album
>>>>>>> 0d81f33... Added threading to mixsetup, Optimize speed of Mixtapes class

### Set Media Player with a Mixtape Album

> - mixtape ablum can be reference either by `index`  or by its  `album name`
>-  index starts at __one (1)__  not __~~zero (0)~~__
```python
media.setMedia('Creative Control')
#OR 
media.setMedia(1) # set media to 'Creative Control'

#TO VIEW ALL AVAILABLE SONGS     
>>> media.songs 
```
<<<<<<< HEAD
 [ 'Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)', 'Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street', "Jay-Z - Jay's Back ASAP", 'Jay-Z - Live In London', 'Jay-Z - Green Magic', 'Jay-Z - Brooklyn Sound Boy', 'Jay-Z - Child Abuse (Prod. By Green Lantern)', 'Jay-Z - Jay-Z Speaks On Green Lantern', 'Jay-Z - Flashy Life', 'Jay-Z - Got Me On My Shit (Prod. By Green Lantern)',..etc ]
=======
 [ 'Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)', 'Jay-Z - Welcome 2 Atla                                                                                                nta V103 Feat. Young Jeezy & DJ Greg Street', "Jay-Z - Jay's Back ASAP", 'Jay-Z - Live In London                                                                                                ', 'Jay-Z - Green Magic', 'Jay-Z - Brooklyn Sound Boy', 'Jay-Z - Child Abuse (Prod. By Green Lan                                                                                                tern)', 'Jay-Z - Jay-Z Speaks On Green Lantern', 'Jay-Z - Flashy Life', 'Jay-Z - Got Me On My Sh                                                                                                it (Prod. By Green Lantern)',..etc ]

--- --
# Find A Song 
<img src="https://www.google.com/url?sa=i&source=images&cd=&ved=2ahUKEwjP_M7noM3mAhUMVd8KHVMrAPMQjRx6BAgBEAQ&url=https%3A%2F%2Fwww.pinterest.com%2Fpin%2F288230444899254713%2F&psig=AOvVaw2Qo2Uv_-KwUf0GU1FxohsW&ust=1577241545675361" width="100" height="100"> Cant find a song??
```python
   media.findSong('green lan')
```

[(1, 'Creative Control'), (36, 'Headliner & Legends (Jay-Z Freestyles) '), (69, 'Power Us Up( Jay-z, Kanye West, Swizz Beatz)'), (172, 'J3 Rocnation '), (254, "Bakin' Session")]

>>>>>>> 0d81f33... Added threading to mixsetup, Optimize speed of Mixtapes class
--- ---
 ### PLAYING SONG
 >- Songs can be played either by referencing the song  **index** or   **name**.  
>- Song's name __do not__ have to be an exact match. 
    

```python
>>> media.play(2)
#or
>>> media.play('Welcome') 
```
 
 ### MEDIA PLAYER CONTROLS
 >Media player can be   `rewind` , `fast-forward` , `pause` ,  `stop` and control __volume__.
 ``` python
 # create an object of the player class
 player = media.player

 # Rewind
player.rewind()
player.rewind(10) # 10 sec behind

# Fast- Forward
player.ffwd()
player.ffwd(10) # fast-forward 10 sec ahead

# Pause
player.pause

# Stop
player.stop # stop song 

# Volume
player.volume(50) # set media volume to 50 
player.volumeDown(5) # set media volume down 5 steps
player.volumeUp(5) # set media volume up 5 steps
 
```

## Download Song or Album

 > **Download song** 
  >- __params__: `song` , `output`, and `rename`
    >>>__song__ - index or name of song.
    >>>__output__ - directory to save song. *(default: current directory)*
    >>>__rename__ - rename song. *(optional)*

> **Download Album**
>- __params__: `output` 
  >>- __output__ - directory to save song. *(default: current directory)*

```python
#Download single song
media.download(2,output="directory_to_save_song") 
 
#Download full album
media.downloadAlbum(output='directory_to_save_album')

=======
```

#### To view all available Mixtape ablums

```python
>>> mix.mixtapes 
['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z: 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard Classics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1', 'Jay-z - Remixes', 'Jay-Z vs. Maloney - The Blue Album [REMixtape] (2011)', 'Best Verses Of - Jay-z', 'The Jay-z Blends', 'The Best Of Jay-z', 'Gotmorespit Instrumentals Vol 3&quot;bringin Jay-z Back&quot; ', 'Reggae Dubz - JAY-Z (F.S.D Production)', 'Mvp Jay-z Mixtape', 'Jay-Z Birthday Tribute - Mini-Mix', "Jay-z Vs Ron Browz - Autotune Ain't Dead 2", 'Dj Elliot Grinch - Nas And Jay-z (the Bqe)', 'Music Addict Radio Vol. 22 (jay-z Edition)', 'Nas Biggie Jay-Z', 'Happy Birthday Jay-Z Mix', 'Best Of Jay-z Vol. 1', 'Lil Wayne Vs Jay-z', 'Jay-Z - The Blend Album', 'Jay-z Classic Collabos', 'Jay-z  - Nautylus Remix & Instrumentals', 'Battmann-50cents V.s Jay-z', 'Jay-z & O.t. - The Blueprint Remixes', 'Jay-z & 9th Wonder', 'Iceburg Chops Presents: Jay-z Chopped & Screwed', 'The Official Jay-z Mixtape', 'Jay-z Double Agenda', 'Power Us Up 3(Jay-z,Kanye West,Swizz Beatz,Lil Wayne)', 'Best Of Jay-z And 50 Cent', 'Mercury Presents Jay-z Covert Carter', 'Desperado Jay-z Ny Giant Instrumental', 'Jay-z - Early Hova', 'Best Rappers Alive Lil Wayne Vs. Jay-z', 'Headliner & Legends (Jay-Z Freestyles) ', 'Nas And Jay-z', 'Vintage Jigga (Best Of Jay-Z)', 'The Red Album (Game vs Jay-Z)', 'Power Us Up( Jay-z, Kanye West, Swizz Beatz)', 'Mgm-jay (mgmt And Jay-z Mashup Album)', 'JAY-Z : The Blueprint Reproduced With Geniusboy Beats: IamGeniusboy Modified Music Theory', 'Jay-Z - West Coast American Gangster', 'Jay-z - Reasonable Doubt Instrumentals ']
```
### Set the Media Player with a mixtape album

> - **mixtape ablum can be reference either by index or by its name**
>- **index starts at one (1)  not ~~zero (0)~~**
```python
media.setMedia('Creative Control')
#OR 
media.setMedia(1)

#VIEW ALL AVAILABLE SONGS     
>>> media.songs 
['Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)', 'Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street', "Jay-Z - Jay's Back ASAP", 'Jay-Z - Live In London', 'Jay-Z - Green Magic', 'Jay-Z - Brooklyn Sound Boy', 'Jay-Z - Child Abuse (Prod. By Green Lantern)', 'Jay-Z - Jay-Z Speaks On Green Lantern', 'Jay-Z - Flashy Life', 'Jay-Z - Got Me On My Shit (Prod. By Green Lantern)',..etc]
```
#### PLAYING SONG
**songs can be played either by index or by song's name** 
        media.play(2)
#### or

media.play('Welcome 2')
