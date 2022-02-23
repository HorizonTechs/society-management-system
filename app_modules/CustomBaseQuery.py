from flask import abort, make_response, jsonify
from flask_sqlalchemy import BaseQuery

class CustomBaseQuery(BaseQuery):
    def get_or_404(self, id):
        row = self.get(id)
        if not row:
            abort(make_response(jsonify(message="Not found"), 404))
        return row