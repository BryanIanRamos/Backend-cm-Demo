from flask import Blueprint, request, jsonify, send_file, url_for
from models.db_models import db, PostsData, Date
from datetime import datetime
import io

post_data_bp = Blueprint('posts_data_tbl', __name__)

@post_data_bp.route('', methods=['GET'])
def get_all_post_data():
    all_posts_data = PostsData.query.all()

    if not all_posts_data:
        return jsonify({'error': 'No data found'}), 404

    response_data = [
        {
            'data_id': post_data.data_id,
            'download_link': url_for('post_data_blueprint.get_post_data', data_id=post_data.data_id, _external=True),
            'created_at': post_data.date_time.created_at.isoformat() if post_data.date_time and post_data.date_time.created_at else None,
            'updated_at': post_data.date_time.updated_at.isoformat() if post_data.date_time and post_data.date_time.updated_at else None
        }
        for post_data in all_posts_data
    ]

    return jsonify({'posts_data': response_data})


@post_data_bp.route('/<int:data_id>', methods=['GET'])
def get_post_data(data_id):
    post_data = PostsData.query.get(data_id)

    if post_data is None:
        return jsonify({'error': 'Data not found'}), 404

    # Return the PDF file
    return send_file(
        io.BytesIO(post_data.data),  # Convert binary data back to file-like object
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'post_data_{data_id}.pdf'
    )


# @post_data_bp.route('/<int:data_id>', methods=['GET'])
# def get_post_data(data_id):
#     post_data = PostsData.query.filter_by(data_id=data_id)

#     date_created

@post_data_bp.route('', methods=['POST'])
def create_post_data():
    # Retrieve the binary data from the request (e.g., file upload)
    data = request.files.get('data')
    
    if data is None:
        return jsonify({'error': 'No data provided'}), 400

    # Check if the file is a PDF
    if data.content_type != 'application/pdf':
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

    # Create or fetch the current date record
    now = datetime.utcnow()
    date_record = Date.query.filter_by(created_at=now.date()).first()
    if not date_record:
        date_record = Date(created_at=now)
        try:
            db.session.add(date_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Create new post data with the date record's ID
    new_post_data = PostsData(
        data=data.read(),  # Read the binary data
        date_id=date_record.date_id
    )

    # Add to the database and commit
    try:
        db.session.add(new_post_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return str(data)

    # return jsonify({'message': 'Post data created successfully', 'data_id': new_post_data.data_id}), 201
