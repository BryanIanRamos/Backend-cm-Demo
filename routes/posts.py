from flask import Blueprint, request, jsonify
from models.db_models import db, Posts, Date
from datetime import datetime

posts_bp = Blueprint('posts_tbl', __name__)

@posts_bp.route('', methods=['GET'])
def get_posts():
    posts = Posts.query.all()

    posts_list = []
    for PT in posts:
        date_created = PT.date_time.created_at if PT.date_time else None
        date_updated = PT.date_time.updated_at if PT.date_time else None
    
        posts_list.append({'post_id': PT.post_id,
                        "content": PT.content, 
                        'date_id': PT.date_id,  
                        'date_created': date_created.isoformat() if date_created else None,
                        'date_updated': date_updated.isoformat() if date_updated else None
                    })
    
    return jsonify(posts_list)

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Posts.query.filter_by(post_id=post_id).first()

    if post is None:
        return jsonify({'error': 'Data not found.'}), 404
    
    # Retrieve the date created from the related Date model
    date_created = post.date_time.created_at if post.date_time else None
    date_updated = post.date_time.updated_at if post.date_time else None
    
    post_list = [{
        'post_id': post.post_id,
        'content': post.content,
        'date_created': date_created.isoformat() if date_created else None,
        'date_updated': date_updated.isoformat() if date_updated else None
    }]

    return jsonify(post_list)


@posts_bp.route('', methods=['POST'])
def register_account():
    content = request.form.get('content')
    account_id = request.form.get('account_id')

    if content is None:
        content = ''

    # Create a new date record with the current time
    now = datetime.utcnow()
    date_record = Date(created_at=now)

    try:
        db.session.add(date_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Create new account with the date record's id
    new_post = Posts(
        content=content,
        account_id=account_id,
        date_id=date_record.date_id,
    )

    # Add to database and commit
    try:
        db.session.add(new_post)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Post created successfully'}), 201


@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Posts.query.get(post_id)

    content = request.form.get("content")

    if content is None:
        content = ''

    if post is None:
        return jsonify({'error': 'Data not found.'}), 404

    # Update the related Date record's updated_at field
    now = datetime.utcnow()

    if post.date_time:  # Ensure that the post has an associated Date record
        post.date_time.updated_at = now
    else:
        # If for some reason there's no related Date record, create one
        new_date_record = Date(updated_at=now)
        db.session.add(new_date_record)
        post.date_id = new_date_record.date_id

    post.content = content

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)})

    return jsonify({'message':'Post have been updated successfully.'}), 200
    

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Posts.query.filter_by(post_id=post_id).first()

    if post is None:
        return jsonify({'error': 'Data not found.'}), 404

    # Store the date_id before deleting the post
    date_id = post.date_id

    try:
        # Delete the post
        db.session.delete(post)
        db.session.commit()

        # Check if any other posts are using the same date_id
        remaining_posts = Posts.query.filter_by(date_id=date_id).all()

        # If no other posts are using this date_id, delete the date record
        if not remaining_posts:
            date_record = Date.query.filter_by(date_id=date_id).first()
            if date_record:
                db.session.delete(date_record)
                db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Post and associated date deleted successfully'}), 200
