import asyncio

from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class AuthMain:

    @staticmethod
    async def run():

        config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")
        async with SymphonyBdk(config_3) as bdk:
            auth_session = bdk.bot_session()
            print(await auth_session.key_manager_token)
            print(await auth_session.session_token)


if __name__ == "__main__":
    asyncio.run(AuthMain.run())
