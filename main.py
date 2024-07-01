from pyrogram import Client
from config import SamawebGradeCheckerConfig
import configparser

# configure plugins
plugins = dict(root="plugins")

# read .env file
config = SamawebGradeCheckerConfig()

api_id = config.api_id
api_hash = config.api_hash
token = config.token

# read proxy file
proxy_config = configparser.ConfigParser()
proxy_config.read('proxy.ini')

proxy = {
    "scheme": proxy_config.get('proxy', 'scheme'),
    "hostname": proxy_config.get('proxy', 'hostname'),
    "port": proxy_config.getint('proxy', 'port'),
}

# Client instance
bot = Client(
    name="mar_gc",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=token,
    plugins=plugins,
    proxy=proxy
)

if __name__ == "__main__":
    bot.run()