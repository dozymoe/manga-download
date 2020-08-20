from aiohttp import request
from aiomultiprocess import Pool
import asyncio
from datetime import datetime
from email.parser import BytesParser
import json
import logging
import os
import pathlib
from PIL import Image, ImageFile
import piexif

ImageFile.LOAD_TRUNCATED_IMAGES = True

_logger = None


def worker_init():
    global _logger
    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(__name__)


async def worker_main(record):
    binargs = [
        'curl',
        '--dump-header', '-',
        '--silent',
        '--continue-at', '-',
        '--create-dirs',
        '--fail',
        # This will be rewritten anyway when we updates EXIF
        #'--remote-time',
        '--connect-timeout', '60',
        '--retry-delay', '10',
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
    etag_path = os.path.join(os.path.dirname(etag_path),
            '.%s' % os.path.basename(etag_path))
    if os.path.exists(etag_path):
        binargs.append('--etag-compare')
        binargs.append(etag_path)
    binargs.append('--etag-save')
    binargs.append(etag_path)

    binargs.append(record['url'])

    proc = await asyncio.create_subprocess_exec(*binargs,
            stdout=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode == 0:
        # read response headers
        status, stdout = stdout.split(b'\r\n', 1)
        headers = BytesParser().parsebytes(stdout)
        return record, status.strip(), headers
    return record, None, None


async def worker_result(record, status, headers):
    if not status:
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
    if img.mode != 'RGB':
        img = img.convert('RGB')
    try:
        exif_dict = piexif.load(img.info['exif'])
    except KeyError:
        exif_dict = {}
    if not 'Exif' in exif_dict:
        exif_dict['Exif'] = {}
    exif_dict['Exif'][piexif.ExifIFD.UserComment] = comic.SerializeToString()
    img.save(pathlib.Path(record['path']).with_suffix('.jpg'), format='JPEG',
            exif=piexif.dump(exif_dict))

    _logger.info(record['path'])
    # Delete download queue
    url = 'http://%s:%s/download-url/delete' % (os.environ['LISTEN_ADDR'],
            os.environ['LISTEN_PORT'])
    async with request('POST', url, data={'id': record['id']}) as response:
        pass


async def worker_execute():
    global _logger
    _logger = logging.getLogger(__name__)

    try:
        url = 'http://%s:%s/download-url/index' % (os.environ['LISTEN_ADDR'],
                os.environ['LISTEN_PORT'])

        while True:
            async with request('GET', url) as response:
                records = await response.json()

            if records:
                async with Pool(4, worker_init) as pool:
                    async for record, status, headers in\
                            pool.map(worker_main, records):
                        await worker_result(record, status, headers)

            await asyncio.sleep(20)
    except asyncio.CancelledError:
        pass
