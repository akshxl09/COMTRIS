'''
COMTRIS Application Config Setting
'''
import os
import sys
from datetime import datetime
from logging.config import dictConfig


BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    '''공통 Config'''
    # Authorization
    SECRET_KEY = os.environ['COMTRIS_SECRET_KEY']
    ADMIN_ID = os.environ['COMTRIS_ADMIN_ID']
    ADMIN_PW = os.environ['COMTRIS_ADMIN_PW']

    # Database
    MONGODB_URI = os.environ['COMTRIS_MONGODB_URI']
    MONGODB_DB_NAME = 'COMTRIS'

    # Maximum API time
    SLOW_API_TIME = 0.5

    # master_config 기본 값
    DEFAULT_MASTER_CONFIG = [
        {
            "key": "COMTRIS_TEST",
            "value": "COMTRIS_TEST"
        }
    ]

    @staticmethod
    def init_app(app):
        '''전역 init_app 함수'''


class TestingConfig(Config):
    '''Test 전용 Config'''
    DEBUG = True
    TESTING = True


class DevelopmentConfig(Config):
    '''개발 환경 전용 Config'''
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    ''' 상용환경 전용 Config'''
    DEBUG = False
    TESTING = False

    @staticmethod
    def init_app(app):
        '''로거 등록 및 설정'''
        dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                }
            },
            'handlers': {
                'file': {
                    'level': 'WARNING',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': os.getenv('COMTRIS_ERROR_LOG_PATH') or './server.error.log',
                    'maxBytes': 1024 * 1024 * 5,
                    'backupCount': 5,
                    'formatter': 'default',
                },
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['file']
            }
        })


config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing':TestingConfig,
    'default':DevelopmentConfig,
}
