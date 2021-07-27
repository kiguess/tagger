from deemix import tagger, settings
from deemix.types import Track
from deemix.utils.pathtemplates import generateTrackName
from deezer import Deezer
from os import path
import os, sys, logging, magic

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('tag.log', 'w'),
        logging.StreamHandler(sys.stdout)
    ]
)

fileloc  = path.join(os.curdir, 'file')
logging.info('Start')

if (not path.exists(fileloc) or path.isfile(fileloc)):
    logging.info('Target folder not found, exitting')
    print('Please put the files in a folder named "file" with track ID as filename')
    exit(1)

loaded_settings = settings.load()
logging.debug(f'Settings loaded:\n{loaded_settings}')
files = [f for f in os.listdir(fileloc) if path.isfile(path.join(fileloc, f))]
logging.debug(f'Found files: {files}')

dz = Deezer()
for file in files:
    try:
        track_id = int(file)
    except ValueError:
        logging.info(f'Invalid name {file}, skipping..')
        continue

    logging.info(f'File: {file}')
    file_path = path.join(fileloc, file)
    file_type = magic.from_file(file_path)
    if (file_type == 'audio/flac' or file_type == 'audio/mpeg'):
        logging.debug(f'File is {file_type}')
    else:
        logging.info(f'Unrecognized mime type {file_type}, skipping..')
        continue
    
    ext   = ''
    track = Track.Track()
    track.parseData(dz, track_id=track_id)
    logging.debug(f'Track recognized as {track.artists} - {track.title}')

    if (file_type == 'audio/flac'):
        tagger.tagFLAC(file_path, track, loaded_settings['tags'])
        ext = '.flac'
    else:
        tagger.tagID3(file_path, track, loaded_settings['tags'])
        ext = '.mp3'
    
    logging.info('Tagging completed')
    filename = generateTrackName(loaded_settings['tracknameTemplate'], track, loaded_settings)

    os.rename(file_path, path.join(fileloc, filename + ext))
    logging.info(f'File renamed as {filename + ext}')

    if loaded_settings['syncedLyrics']:
        if not track.lyrics.sync:
            logging.debug('Synced lyric not available')
        else:
            lrcfile = path.join(fileloc, filename + '.lrc')
            with open(lrcfile, 'wb') as f:
                f.write(track.lyrics.sync.encode('utf-8'))
            logging.info('lrc file created')
    
    logging.info(f'Done with {file}')

logging.info('Done')