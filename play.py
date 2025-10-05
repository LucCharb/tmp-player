# dependencies: python-mutagen, clyrics, mpv
import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.dsf import DSF
import subprocess
import sys
import tty
import termios
import random
import re
import requests
import getpass

def play_songs(media_result):
    try:
        for i in media_result:
            lyrics=get_lyrics(i)
            if lyrics != None:
                print(lyrics)            
            args = ["mpv", "--no-video","--no-sub", "--vo=null", "--msg-level=cplayer=error", "--gapless-audio=yes", i]
            subprocess.run(args, check=True)
    except KeyboardInterrupt:
        return

def play_show(show):
    try:
        # args = ["mpv", "--vo=kitty", "--no-sub", "--msg-level=cplayer=error", "--really-quiet", show]
        args = ["mpv", "--no-sub", "--msg-level=cplayer=error", "--really-quiet", show]
        subprocess.run(args, check=True)
    except (KeyboardInterrupt, subprocess.CalledProcessError):
        return

def get_lyrics(file):
    new_file_path = None
    new_file_path=checklyrics_exist(file)
    if new_file_path != None:
        with open(new_file_path, "r") as f:
          lyrics = f.read()
        return lyrics
    else:
        a=os.path.basename(file)
        b = os.path.splitext(a)[0]
        c = b.split(' - ')
        if len(c) == 3:
            c[1]=c[2]
        # arg=['clyrics', c[0],c[1]]
        # arg=['lyrics', '-t', c[0],c[1]]
        lyrics = fetch_lyrics(c[0],c[1])
        if lyrics != None:
            lyrics = lyrics.replace("\n\n", "\n")
            print("\033c", end="")
            print("Playing ",c[0]," - ",c[1],"\n")
            print(lyrics,"\n")
            root, ext = os.path.splitext(file)
            new_file_path = root + ".txt"
            try:
                with open(new_file_path, "w") as f:
                    f.write(lyrics)
            except Exception as e:
                return
    return None

def fetch_lyrics(artist, title):
    # Construct the API URL
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    
    try:
        # Send a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Check if lyrics are available
        if "lyrics" in data:
            return data["lyrics"]
        else:
            return "Lyrics not found."
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def checklyrics_exist(file):
    ext=['.txt','.lrc']
    for ex in ext:
        oldfile_name = os.path.splitext(file)
        new_file_path = f"{oldfile_name[0]}{ex}"  
        if os.path.exists(new_file_path) == True:
            return new_file_path
    return None

def go_back(media_result):
    print("\033c", end="")
    list_songs(media_result)    

def playOne(choice_index,media_result):
    list=[]
    list.append(songs_tuple[choice_index][1])
    play_songs(list)
    print("\033c", end="")
    list_songs(media_result)
    main()

def playAll(media_result):
    list=[]
    for i in songs_tuple:
        list.append(i[1])
    play_songs(list)
    go_back(media_result)    

def shuffle(media_result):
    mylist = [i for i in range(len(songs_tuple))]
    list=[]
    random.shuffle(mylist)
    for i in mylist:
        list.append(songs_tuple[i][1])        
    play_songs(list)       
    go_back(media_result)
    
def quit(*args):
    main()  

def fromTo(media_result): 
    fromTo=input('Enter From to numbers separated by a comma:')
    print(f"You chose {fromTo}")  
    ftlist = [int(item) for item in fromTo.split(",")]
    list=[]
    for i in range(ftlist[0]-1,ftlist[1]):
        list.append(songs_tuple[i][1])
    play_songs(list)
    go_back(media_result)
    
def multi(media_result):
    multi=input('Enter numbers separated by a comma:')
    print(f"You chose {multi}")  
    ftlist = [int(item) for item in multi.split(",")]
    list=[]
    for i in (ftlist):
        list.append(songs_tuple[i-1][1])
    play_songs(list)
    go_back(media_result)
    
def to_exit():
    subprocess.run("clear")
    # subprocess.run("pfetch")    
    exit()

def input_song(media_result):
    choices=('A','F','S','M','Q')
    opt = {"A":playAll,"F":fromTo,"S":shuffle,"M":multi,"Q":quit}
    choice=""
    while True:
        choice = input()
        if is_number(choice) == True:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(media_result):
                playOne(choice_index,media_result)
            else:
                print('Value is wrong, try again.')
                # input()
        else:
            choice = choice.upper()
            if choice not in choices:
                print('Value is wrong, try again.')
            else:    
                action=opt[choice]
                action(media_result)
                input_song(media_result)        


def settings():
    inp_list=('1','2','q','Q')
    display_menu("set")
    sel = get_char()
    if sel not in inp_list:
        print("Invalid input. Please enter a valid option.", end="")
        input()
        settings()
    if sel.lower() == 'q':
        main()
    try:
        sel = int(sel)
    except ValueError:
        print("Invalid input. Please enter a valid option.")
        input()
        settings()
    if sel==1:
        query = ' SELECT * FROM Sources '
        source=go_db(query)
        inp(source)
    elif sel==2:
        print("Scanning libraries, please don't interupt...")
        scan_db()
        ans=input('Scan completed. Exit? (y,n)')
        if ans.lower() == 'y':
            main()
        else:
            settings()

def inp(source):
    c=0
    if source:
        for line in source:
            c+=1
            lineup=str(c)+' - '+line[1]+' - '+line[2]
            d=60-len(lineup)
            print("#    "+ lineup + " " * d +"#")
    else:
        print(' No Media Sources Available')

    print(' ' + '=' * 64 + ' ')
    print("1-)Add source - 2-)Remove source - Q-)Go back" )
    source_path = get_char()
    match source_path:
        case '1':
            men = {"1":"Music","2":"Shows","3":"Movies"}
            mt=input("Media type? (1-Music - 2-Shows - 3-Movies) " )
            media_path=input("Enter source path: ")
            query = 'INSERT INTO Sources (media,source)VALUES(?,?)'
            source=go_db(query,(men[mt],media_path))
            print(source)
        case '2':
            i=int(input(f"Enter number for 1 to {len(source)} :"))
            query='DELETE FROM Sources WHERE media=? AND source=?'
            go_db(query,(source[i-1][1],source[i-1][2]))
        case _:
            settings()
    query = ' SELECT * FROM Sources '
    source=go_db(query)
    display_menu('set')
    inp(source)

def list_songs(media_result):
    global songs_tuple
    songs_tuple=[]
    key = {'id':0, 'artist':1, 'album':2, 'track':3, 'title':4, 'genre':5, 'path':6}
    dir_album=""
    for i, song in enumerate(media_result):
        if mode != "title" and song[key['album']] != dir_album:
            dir_album=song[key['album']]
            print(" ")
            print(dir_album)                    
            print("#####media_result##################################")
        print(f"{i+1}. {song[key['artist']]} - {song[key['title']]} - [{song[key['genre']]}]")
        songs_tuple.append((i, song[key['path']]))
    display_menu("after")
    input_song(media_result)

def list_shows(media_result):
    """List TV shows from media_result, printing title and season when both are new, season only when it changes."""
    show_tup = []
    current_title = ""
    current_season = None
    count = 0
    # print("")
    for file in sorted(media_result):
        new_title = file[1].split('/')[5]  # Extract title

        try:
            episode = file[2]
            result = test(episode)
            season = result["season"]

            # New title: print title and season
            if new_title != current_title:
                current_title = new_title
                current_season = season  # Reset season for new title
                print("\n")
                print("-----------------------------------")
                print(f"Show: {current_title}")
                print(f"Season {season}")
                print("-----------------------------------")
            # Same title, new season: print only season
            elif season != current_season:
                current_season = season
                print("")
                print(f"Season {season}")
                print("-----------------------------------")

            # Print episode
            print(f"{count} - {episode}")
            show_tup.append((count, file[1]))
            count += 1

        except ValueError as e:
            print(f"Error: {e}")

    return show_tup
def list_movies(media_result):
    count=0
    show_tup=[]
    print('#' * 60)
    print(' '*22+'Movies Available')
    print('_'*60)
    for file in sorted(media_result):
        try:
            tvs=file[2]
            ct=str(count)
            print(ct + ' - ', end="")
            print(tvs)
            show_tup.append((count, file[1]))
            count += 1
        except ValueError as e:
            print(e)
    return show_tup

def main():
    try:
        display_menu("main")
        mode_select=""
        choices=("1","2","3","4","5","6", "S","s","Q","q")
        men = {"1":"title","2":"artist","3":"album","4":"genre","5":"show","6":"movie","s":"setting","q":"quit"}
        print("Enter:")
        while mode_select not in choices:
            mode_select = get_char()
        mode_select=mode_select.lower()
        global mode
        mode = men[mode_select]
        query=''
        match mode_select:
            case 's':
                settings()
            case 'q':
                to_exit()


        find_in_db = input(f"What {mode}? ('q' = back): ")
        if find_in_db.lower() == 'q':
            main()

        cur=connect_db()    
        match mode:
            case 'show':
                query = f'SELECT * FROM Shows WHERE show LIKE ?'
            case 'movie':
                query = f'SELECT * FROM Movies WHERE movie LIKE ?'     
            case _:
                query = f'SELECT * FROM Music WHERE {mode} LIKE ?'
        cur.execute(query, ("%{}%".format(find_in_db),)) 
        media_result = cur.fetchall()

        close_db() 
        
        if not media_result:
            print(f"No media found for that {mode}.")
            input()
            main()
        else:
            match mode:
                case 'show':
                    main_shows(list_shows,media_result)
                case 'movie':
                    main_shows(list_movies,media_result)
                case _:
                    list_songs(media_result)
    except KeyboardInterrupt:
        to_exit()

def go_db(query, *args):
    try:
        media_result='yeah'
        cur=connect_db()
        cur.execute(query, *args)        
        media_result = cur.fetchall()
        close_db()
        return media_result
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return
    
def main_shows(args,media_result):
    show_tup=args(media_result)
    while True:
        choice=input(f'Chose a number from 1 to {len(media_result)-1} or "q" to quit)')
        if choice.lower()=="q":
            main()
        if is_number(choice):
            choice = int(choice)
            if 0 <= choice < len(media_result):
                toPlay = show_tup[choice][1]
                play_show(toPlay)
                main_shows(args,media_result)
            else:
                print("Invalid selection. Try again.")
    main()


def display_menu(menu):
    match menu:
        case "main":
            print("\033c", end="")
            print("##################################################################")
            print("                        CH2o Media Player                         ")
            print("    1-)Song       2-)Artist     5-)TV-Shows          S-)Settings  ")
            print("    3-)Album      4-)Genre      6-) Movies           Q-)Quit      ")
            print("##################################################################")
        case "after":
            print("##################################################################")
            print("  play a song(enter number)               A-)Play all             ")
            print("  S-)Play all shuffled   M-)Play multiple   F-)play From-to       ")
            print("                           Q-)go back                             ")
            print("##################################################################")      
        case "scan":
            print("\033c")
            print("##################################################################")
            print("                       Scan library will start                    ")
            print("     Do NOT interrupt the process(you'll have to restart it)      ")
            print("                       (P)-Proceed or quit-(Q)                    ")
            print("##################################################################")                  
        case "set":
            print("\033c", end="")
            print("##################################################################")
            print("                        CH2o Media Player                         ")
            print("    1-)Library sources                      2-)Scan library       ")
            print("                                                     Q-)Quit      ")
            print("##################################################################")


def test(file):
    pattern = r"^(.*?)\s?[-–]?\s?[Ss](\d{1,2})[Ee](\d{1,2})\s?[-–]?\s?(.*?)\.(mkv|mp4|avi)$"
    match = re.match(pattern, file)
    if match:
        show = match.group(1).strip()
        season = match.group(2)
        episode = match.group(3)
        title = match.group(4).strip()
        return {
        "show": show,
        "season": season,
        "episode": episode,
        "title": title
        }
    else:
        raise ValueError('Error' + file)

def extract_genre(file_path):
    if file_path.endswith('.mp3'):
        audio = MP3(file_path)
    elif file_path.endswith('.flac'):
        audio = FLAC(file_path)
    elif file_path.endswith('.wav'):
        audio = WavPack(file_path)
    elif file_path.endswith('.dsf'):
        audio = DSF(file_path)
    else:
        print(file_path)
        print("Unsupported file format")
        return

    genre = audio.get('genre')
    return genre

def is_number(value):
  try:
    int(value)
    return True
  except ValueError:
    return False

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        if not sys.stdin.closed:  # Check if the file is closed
            ch = sys.stdin.read(1)
        else:
            ch = ''  # Handle closed file scenario
    except Exception as e:
        ch = ''  # Handle closed file scenario
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def scan_music(args):
    cur = connect_db()

    for root,dirs, files in os.walk(args):
            split_root = root.split('/')
            folder=split_root[-1]
            for file in sorted(files):
                try:
                    if file.endswith(('.mp3', '.wav', '.flac','.dsf')):  
                        parts = file.split(' - ')
                        # Insert data into the SQLite database
                        song=[part.strip() for part in parts if part.strip()]
                        par=len(song)
                        artist=parts[0]
                        album=folder
                        if par > 1:
                            if par < 3: 
                                track=""
                                title=parts[1]
                            else:
                                track=parts[1]
                                title=parts[2]
                            path=root + "/" + file
                            genres=extract_genre(path)
                            if genres is not None: 
                                genre =''.join(genres) 
                            else: 
                                genre="unknow"
                            # print(".", end="")
                            cur.execute('''INSERT INTO Music (artist, album, track, title, genre, path)
                                        VALUES (?, ?, ?, ?, ?, ?)''', (artist, album, track, title, genre, path))
                except Exception as e:
                    continue
    close_db()

def scan_show(args):
    cur = connect_db()

    for root,dirs, files in sorted(os.walk(args)):
            for file in sorted(files):
                try:
                    if file.endswith(('.mp4', '.mkv', '.webm','.avi')):  
                        # print(".", end="")
                        path = root + "/" + file
                        cur.execute('''INSERT INTO Shows (path, show) VALUES (?, ?)''', (path, file))
                except Exception as e:
                    continue                    
    close_db()

def scan_movie(args):
    cur = connect_db()
    
    for root,dirs, files in sorted(os.walk(args)):
            for file in sorted(files):
                try:
                    if file.endswith(('.mp4', '.mkv', '.webm','.avi')):  
                        # print('.', end="")
                        path = root + "/" + file
                        cur.execute('''INSERT INTO Movies (path, movie) VALUES (?, ?)''', (path, file))
                except Exception as e:
                    continue   
    close_db()

def scan_db():
    column={'Music':scan_music,'Shows':scan_show,'Movies':scan_movie}
    query=f'SELECT * FROM Sources'
    db_sources = go_db(query,"")
    if db_sources:
        tables=('Music', 'Shows', 'Movies')
        for table in tables:
            query=f'DELETE FROM {table}'
            go_db(query,'')
        for sour in db_sources:
            column[sour[1]](sour[2])

def connect_db():
  user = getpass.getuser()
  current_dir = os.getcwd()
  myMedia="/app/data/myMedia.db"
  global conn
  conn = sqlite3.connect(myMedia)
  cur = conn.cursor()
  return cur

def close_db():
  conn.commit()
  conn.close()

def arg_func(arg):
    query = f'SELECT * FROM Music WHERE title LIKE ?'
    cur=connect_db()
    cur.execute(query, ("%{}%".format(arg),))
    media_result=cur.fetchall()
    close_db()
    if not media_result:
        print(f"No songs found for that title.")
        input()
        main()
    else:
        if len(media_result)==1:
            result=[(media_result[0][-1])]
            play_songs(result)
        else:
            list_songs(media_result)
            to_exit()
        return 
    
try:
    arg = sys.argv[1]
    arg_func(arg)
except: ValueError()

query1 = 'CREATE TABLE IF NOT EXISTS Music ( id INTEGER PRIMARY KEY, artist TEXT, album TEXT, track TEXT, title TEXT, genre TEXT, path TEXT )'
query2 = 'CREATE TABLE IF NOT EXISTS Shows ( id INTEGER PRIMARY KEY, path TEXT, show TEXT )'
query3 = 'CREATE TABLE IF NOT EXISTS Movies ( id INTEGER PRIMARY KEY, path TEXT, movie TEXT )'
query4 = 'CREATE TABLE IF NOT EXISTS Sources ( id INTEGER PRIMARY KEY, media TEXT, source TEXT )'
queries = [query1,query2,query3,query4]
for i in queries:
    go_db(i,"")

main()
# if __name__ == "__main_music__":

