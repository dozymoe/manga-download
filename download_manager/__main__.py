from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
import logging
import os
import subprocess
#-
from .core.database import open_sqlite, close_sqlite
from .download_url.views import download_url_create, download_url_destroy
from .download_url.views import download_url_index, download_url_edit
from .download_worker import start_workers, stop_workers, clean_workers

logging.basicConfig(level=logging.DEBUG)

protobuf_dir = os.path.join(os.path.dirname(__file__), 'protobuf')
generated_dir = os.path.join(os.path.dirname(__file__), 'generated')
subprocess.check_call(
        [
            'protoc',
            '--proto_path=%s' % protobuf_dir,
            '--python_out=%s' % generated_dir,
            'download_url.proto',
        ])

app = web.Application()
app['config'] = {
    'database_name': os.path.join(os.environ['ROOT_DIR'], 'var',
        'download_manager.db'),
}

app.router.add_get('/download-url/index', download_url_index)
app.router.add_post('/download-url/add', download_url_create)
app.router.add_post('/download-url/edit', download_url_edit)
app.router.add_post('/download-url/delete', download_url_destroy)

app.on_startup.append(open_sqlite)
app.on_cleanup.append(close_sqlite)

app.on_startup.append(start_workers)
app.on_shutdown.append(stop_workers)
app.on_cleanup.append(clean_workers)

app.middlewares.append(validation_middleware)
setup_aiohttp_apispec(app=app, title="Download Manager", version="v1")
web.run_app(app, host=os.environ['LISTEN_ADDR'], port=os.environ['LISTEN_PORT'])
