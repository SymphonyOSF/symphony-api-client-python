import asyncio
import logging.config
import os

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
        logging.info("Obo example:")
        obo_auth_session = bdk.obo(username="username")
        logging.info(await obo_auth_session.session_token)


logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + '/logging.conf',
                          disable_existing_loggers=False)

asyncio.run(run())
