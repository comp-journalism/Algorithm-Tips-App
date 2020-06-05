from flask import jsonify


def abort_json(status, reason=None):
    inner_res = {
        'status': 'error',
    }
    if reason is not None:
        inner_res['reason'] = reason

    res = jsonify(inner_res)
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
