import binascii
from pyramid.session import BaseCookieSessionFactory
from pyramid_nacl_session import EncryptedCookieSessionFactory

def includeme(config):
    settings = config.get_settings()
    hex_secret = settings['session.session_secret'].strip()
    secret = binascii.unhexlify(hex_secret)
    factory = EncryptedCookieSessionFactory(secret)  # other config ad lib.
    config.set_session_factory(factory)
