
class MissingEnvironmentVariablesException(Exception):
    """Raise if a required environment variable is not set."""
    
    def __init__(self, env_vars : list[str]):
        msg = "you need to set env variables(s) " + ", ".join(env_vars)
        super().__init__(msg)