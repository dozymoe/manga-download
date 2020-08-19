from aiohttp import request
from aiomultiprocess import Pool
import asyncio
from datetime import datetime
#from email.parser import BytesParser
import json
import logging
import os
import pathlib
from PIL import Image
import piexif

_logger = logging.getLogger(__name__)


async def worker_main(record):
    _logger.info('worker_main:curl')
    binargs = [
        'curl',
        '--dump-header', '-',
        '--silent',
        '--continue-at', '-',
        '--create-dirs',
        '--fail',
        '--parallel',
        # This will be rewritten anyway when we updates EXIF
        #'--remote-time',
        '--connect-timeout', '30',
        '--retry-delay', '0',
        '--retry', '99',
        '--output', record['path'],
    ]

    # referer
    if record.get('http_referer'):
        binargs.append('--referer')
        binargs.append(record['http_referer'])

    # user agent
    if record.get('http_user_agent'):
        binargs.append('--user-agent')
        binargs.append(record['http_user_agent'])

    # cookies
    if record.get('cookie_jar'):
        binargs.append('--cookie-jar')
        binargs.append(record['cookie_jar'])

    # auth
    if record.get('auth_username'):
        binargs.append('--user')
        binargs.append('%s:%s' % (record['auth_username'],
                record.get('auth_password', '')))

    # e-tag
    etag_path = pathlib.Path(record['path']).with_suffix('.etag')
    if os.path.exists(etag_path):
        binargs.append('--etag-compare')
        binargs.append(etag_path)
    binargs.append('--etag-save')
    binargs.append(etag_path)

    binargs.append(record['url'])

    proc = await asyncio.create_subprocess_exec(*binargs,
            stdout=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    ## read response headers
    #status, stdout = stdout.split(b'\r\n', 1)
    #headers = BytesParser().parsebytes(stdout)

    result = proc.returncode == 0
    _logger.info('worker_main:result:%s' % result)
    return record, result


async def worker_result(record, result):
    _logger.info('worker_result')
    if not result:
        # Update download queue and exit
        url = 'http://%s:%s/download-url/edit' % (os.environ['LISTEN_ADDR'],
                os.environ['LISTEN_PORT'])
        data = {
            'id': record['id'],
            'retries': record['retries'] + 2,
            'downloaded_at': datetime.now().isoformat(),
        }
        _logger.info('worker_result:POST edit')
        async with request('POST', url, data=data) as response:
            pass
        return

    _logger.info('worker_result:POST delete')
    # Delete download queue
    url = 'http://%s:%s/download-url/delete' % (os.environ['LISTEN_ADDR'],
            os.environ['LISTEN_PORT'])
    async with request('POST', url, data={'id': record['id']}) as response:
        pass

    # Generate bytes representation of Comic metadata
    from ..generated import ComicChapterMeta
    meta = json.loads(record.get('meta', '{}'))
    comic = ComicChapterMeta()
    for field in ['serie', 'title']:
        if not field in meta or not meta[field]:
            continue
        setattr(comic, field, meta[field])
    for field in ['volume', 'chapter', 'chapter_extra']:
        if not field in meta or not meta[field]:
            continue
        setattr(comic, field, int(meta[field]))


    # Store Comic metadata as EXIF
    img = Image.open(record['path'])
    exif_dict = piexif.load(img.info['exif'])
    if not 'Exif' in exif_dict:
        exif_dict['Exif'] = {}
    exif_dict['Exif'][piexif.ExifIFD.UserComment] = comic.SerializeToString()
    img.save(pathlib.Path(record['path']).with_suffix('.jpg'), 'jpeg',
            exif=piexif.dump(exif_dict))


async def worker_execute():
    _logger.info('worker_execute')
    try:
        url = 'http://%s:%s/download-url/index' % (os.environ['LISTEN_ADDR'],
                os.environ['LISTEN_PORT'])

        while True:
            async with request('GET', url) as response:
                records = await response.json()

            if records:
                async with Pool(3) as pool:
                    async for record, result in pool.map(worker_main, records):
                        await worker_result(record, result)

            await asyncio.sleep(10)
    except asyncio.CancelledError:
        _logger.info('worker_execute:cancel')
        pass
