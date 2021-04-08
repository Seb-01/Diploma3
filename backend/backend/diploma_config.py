# Хороший код!
from django.core.exceptions import ImproperlyConfigured
import os

def get_env_var(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable!"
        raise ImproperlyConfigured(error_msg)
