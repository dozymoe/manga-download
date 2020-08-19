from .worker_manager import worker_execute


async def start_workers(app):
    app['worker_task'] = app.loop.create_task(worker_execute())


async def stop_workers(app):
    app['worker_task'].cancel()


async def clean_workers(app):
    await app['worker_task']
