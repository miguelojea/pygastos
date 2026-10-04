import json5


class Secrets:
    def __init__(self, filepath='private/secrets.json'):
        with open(filepath) as f:
            data = json5.load(f)
        self.hashed_password = data.get('hashed_password')


# Instancia global para usar en toda la app
secrets = Secrets()
