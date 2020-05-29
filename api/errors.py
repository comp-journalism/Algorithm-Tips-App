from flask import jsonify


def abort_json(status, reason):
    res = jsonify({
        'status': 'error',
        'reason': reason
    })
    res.status_code = status
    return res


class LocalError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class ConfirmationPendingError(LocalError):
    pass


class NoSuchConfirmation(LocalError):
    pass
