from flask import Blueprint, request, jsonify
from models.db_models import db, Date
from werkzeug.security import generate_password_hash

date_created_bp = Blueprint('date_created_tbl', __name__)

@date_created_bp.route('', methods=['GET'])
def get_dates_created():
    date_created = Date.query.all()
    date_list = [{'date_id': DT.date_id, "created_at": DT.updated_at, "updated_at": DT.created_at} for DT in date_created]

    return jsonify(date_list)

@date_created_bp.route('/<int:date_id>', methods=['GET'] )
def get_date_created(date_id):
    date = Date.query.get(date_id)

    if date is None:
        return jsonify({'error': 'Data not found.'}), 404

    date_list = [{
        'date_id' : date.date_id,
        'created_at' : date.created_at,
        'updated_at' : date.updated_at
    }]

    return jsonify(date_list)