
# PyDatPiff
![alt text](https://i-love-png.com/images/c7ce1da7ed7ace50867927d6a6520e62.png)

[![Build Status](https://travis-ci.com/cbedroid/Datpiff.svg?token=MfxUXqtaex7vkTXGGmqu&branch=master)](https://travis-ci.com/cbedroid/Datpiff)

# Introduction :
#### PyDapiff - is a python program that interact with Datpiff Mixtapes 
  - supports windows,mac,and linux
  - python 3.4 - above 
   
### Dependencies:
- see requirements:  [requirements.txt](https://github.com/cbedroid/Datpiff/blob/master/requirements.txt) 
- __VLC__ - Datpiff requires the  installation of VLC 
 
### Installation

PyDatpiff requires:  **python3.4 - above** .
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
|__"celebrated"__	| Top ranking celebrity mixtapes 		
|__"popular"__		| Popular mixtapes  available   
|__"exclusive"__	| Exclusive mixtapes 
|__"most download"__| Most downloaded mixtapes
|__"most listen"__	| Most listen mixtapes
|__"most favorite"__| Favorite mixtapes 
|__"highest rating"__| Mixtapes with the highest rating
---

```python 
import Datpiff
mix = Datpiff.Mixtapes(category='hot')

#OR

#search for an artist mixtapes
mix = Datpiff.Mixtapes(search='Jay-Z')
```
# Media 
`Datpiff.Media` -  is class that controls the Datpiff Media Player.
>#### THINGS YOU CAN DO: 
>> - `play`  - plays songs from album
>> - `download` - download song
>>- `downloadAlbum` - download all songs from mixtape album

#### Now Initailize Media class

```python
import Datpiff

mix = Datpiff.Mixtapes(search='Jay-Z')
# we pass in Mixtapes' instance to the Media class
media = Datpiff.Media(mix)


#### To view all available Mixtapes Ablums
>>> mix.mixtapes 
```
    ['Creative Control', 'Carter Collection (15th Anniversary)', 'Viva La Hova', 'The Best Of Jay-z: 25th Anniversary', 'Jay-z - If I Should Die Vol. 1 (the Best Of Jay-z)', 'Jay-Z: The Unheard Classics', 'Jay-z Underground Mixes And Mashes Disk 2', 'Iceburgz Ent Dj Smokeshop Presents -big Tingz-pt.1 Classic Beefs Nas,jay-z And More', 'The Best Of Jay-z Old Vs New', 'The Best Of Jay-z & Biggie Smalls', 'Jay-z Live From Glastonbury ', 'Jay-z Underground Mixes And Mashes disk 1', 'Jay-z - Remixes',..etc ]

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
 [ 'Jay-Z - Intro', 'Jay-Z - Advantage Carter (Prod. By Green Lantern)', 'Jay-Z - Welcome 2 Atlanta V103 Feat. Young Jeezy & DJ Greg Street', "Jay-Z - Jay's Back ASAP", 'Jay-Z - Live In London', 'Jay-Z - Green Magic', 'Jay-Z - Brooklyn Sound Boy', 'Jay-Z - Child Abuse (Prod. By Green Lantern)', 'Jay-Z - Jay-Z Speaks On Green Lantern', 'Jay-Z - Flashy Life', 'Jay-Z - Got Me On My Shit (Prod. By Green Lantern)',..etc ]
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

