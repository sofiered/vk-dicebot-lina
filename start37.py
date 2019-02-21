import asyncio
import os

from logging import config, getLogger

from vk_dice_roll.lina import Lina


async def main():
    if 'HEROKU_APP' in os.environ:
        app_id = os.environ.get('APP_ID')
        login = os.environ.get('LOGIN', '')
        password = os.environ.get('PASSWORD', '')
        secret_key = os.environ.get('SECRET_KEY')
        admin_id = int(os.environ.get('ADMIN_KEY'))
    else:
        import local_settings
        app_id = local_settings.APP_ID
        login = local_settings.LOGIN
        password = local_settings.PASSWORD
        secret_key = local_settings.SECRET_KEY
        admin_id = local_settings.ADMIN_KEY
        log_config = local_settings.LOG_CONFIG

        config.dictConfig(log_config)

    lina = Lina(app_id=app_id,
                login=login,
                password=password,
                admin_id=admin_id,
                secret_key=secret_key,
                names=('моли', 'молли'),
                logger=getLogger('lina'))

    await lina.start()


if __name__ == '__main__':
    asyncio.run(main())
