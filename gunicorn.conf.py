import logging

workers = 4  # Adjust based on CPU cores
bind = "0.0.0.0:10000"
timeout = 120

# Set up logging
gunicorn_logger = logging.getLogger('gunicorn.error')
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stdout
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
        },
    },
    'formatters': {
        'generic': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'loggers': {
        'gunicorn.error': {
            'level': loglevel,
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
