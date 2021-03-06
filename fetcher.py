import libtorrent
import time 
import os
import datetime
import platform
import vlc
import multiprocessing as mp

from qtfaststart.processor import get_index
from qtfaststart.exceptions import FastStartException


def __clear_command():
    os_type = platform.system()
    if os_type=="Windows":
        os.system('cls')
    else:
        os.system('clear')

def __get_file_name(handler):
    return handler.get_torrent_info().name()

def __play_video(filename):
    time.sleep(40)
    __full_file_path__ = os.path.join(os.getcwd(),'downloads',filename)
    
    player = vlc.MediaPlayer(__full_file_path__)
    player.play()

def __fetcher__(link):
    clear = __clear_command()
    session = libtorrent.session()
    session.listen_on(6881,6892)
    params = {
        'save_path':os.path.join(os.getcwd(),'downloads'),
        'storage_mode':libtorrent.storage_mode_t(2),
    }

    handler = libtorrent.add_magnet_uri(session,link,params)
    session.start_dht()

    begin = time.time()
    print(datetime.datetime.now())

    print ('Downloading Metadata...')
    while (not handler.has_metadata()):
        time.sleep(1)
    print ('Got Metadata, Starting Torrent Download...')

    print("Starting", handler.name())

    __started_playing__ = False
    
    pool = mp.Pool(processes=2)

    while (handler.status().state != libtorrent.torrent_status.seeding):

        time.sleep(0.5)
        __clear_command()
        s = handler.status()
        handler.set_sequential_download(True)

        state_str = ['queued', 'checking', 'downloading metadata', \
                'downloading', 'finished', 'seeding', 'allocating']
        print ('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s ' % \
                (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state]))

        if(not __started_playing__):
            pool.apply_async(__play_video,[__get_file_name(handler)])
            __started_playing__ = True

    end = time.time()
    print(handler.name(), "COMPLETE")

    print("Elapsed Time: ",int((end-begin)//60),"min :", int((end-begin)%60), "sec")
    print(datetime.datetime.now())  

if __name__=='__main__':
    __fetcher__("magnet:?xt=urn:btih:470472B7A2E0B60F4939E49D2A1B750C88C4BAAD")