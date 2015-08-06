# -*- coding: utf8 -*-

from __future__ import unicode_literals

from flask import jsonify
from app import app


@app.errorhandler(400)
def bad_request_handler(e):
    app.logger.info(str(e))
    content = {'message': 'The server did not understand your request.'}
    return jsonify(content), 400


@app.errorhandler(401)
def unauthorized_handler(e):
    content = {'message': 'Could not verify your access level for that URL.'}
    return jsonify(content), 401


@app.errorhandler(404)
def not_found_handler(e):
    content = {'message': 'The requested resource could not be found.'}
    return jsonify(content), 404


@app.errorhandler(405)
def method_not_allowed_handler(e):
    content = {'message': 'This method is not allowed for the requested URL.'}
    return jsonify(content), 405


@app.errorhandler(500)
def internal_server_error_handler(e):
    app.logger.warning(str(e))
    content = {'message': 'The server has either erred or is incapable '
                          'of performing the requested operation.'}
    return jsonify(content), 500
