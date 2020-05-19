"""Connect to mysql db using keys.conf"""
import configparser
import subprocess

config = configparser.ConfigParser()
config.read("keys.conf")

subprocess.run(['mysql', 
                f"--user={config.get('AWSDatabaseConfig', 'username')}",
                f"--password={config.get('AWSDatabaseConfig', 'password')}",
                f"--host={config.get('AWSDatabaseConfig', 'host')}",
                f"--database={config.get('AWSDatabaseConfig', 'database')}"])
