from aiohttp import web
from aiohttp_apispec import request_schema
from datetime import datetime
import logging
import os
import shutil
import subprocess
from .requests import DownloadUrlCreateRequest, DownloadUrlDestroyRequest
from .requests import DownloadUrlUpdateRequest

_logger = logging.getLogger(__name__)


@request_schema(DownloadUrlCreateRequest)
async def download_url_create(request):
    _logger.info('download_url_create')
    submission = request['data']
    db = request.app['db']
    await db.execute('''
INSERT INTO download_url(url, path, http_user_agent, http_referer,
    auth_username, auth_password, cookie_jar, meta,
    created_at, retries)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''         ,
            (submission['url'], submission['path'],
            submission.get('http_user_agent'), submission.get('http_referer'),
            submission.get('auth_username'), submission.get('auth_password'),
            submission.get('cookie_jar'), submission.get('meta'),
            datetime.now(), 0))

    return web.Response()


@request_schema(DownloadUrlDestroyRequest)
async def download_url_destroy(request):
    _logger.info('download_url_destroy')
    submission = request['data']
    id = submission['id']

    db = request.app['db']
    await db.execute('DELETE FROM download_url WHERE id=?', (id,))
    return web.Response()


@request_schema(DownloadUrlUpdateRequest)
async def download_url_edit(request):
    _logger.info('download_url_edit')
    submission = request['data']
    id = submission['id']

    db = request.app['db']
    await db.execute('''
UPDATE download_url
    SET retries=?, downloaded_at=?
    WHERE id=?'
'''        ,
           (submission['retries'], submission['downloaded_at'], id))
    return web.Response()


async def download_url_index(request):
    _logger.info('download_url_index')
    db = request.app['db']
    cursor = await db.execute('''
SELECT * FROM download_url
    ORDER BY retries ASC , created_at ASC
    LIMIT 100
''')
    rows = [dict(x) for x in await cursor.fetchall()]
    _logger.info(rows)
    return web.json_response(rows)
