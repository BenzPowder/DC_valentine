import logging

workers = 4  # Adjust based on CPU cores
bind = "0.0.0.0:10000"
timeout = 120

# Use default Gunicorn logging settings
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stdout
