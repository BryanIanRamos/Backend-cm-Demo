from flask import Blueprint, request, jsonify
from models.db_models import db, Accounts, Date
from werkzeug.security import generate_password_hash
from datetime import datetime
from dateutil import parser
from decorators.authUdecorator import token_required

accounts_bp = Blueprint('accounts_tbl', __name__)

@accounts_bp.route('', methods=['GET'])
@token_required
def get_accounts():
    accounts = Accounts.query.all()

    if not accounts:
        return jsonify({'error': 'There is no account registered in the database.'}), 404

    response_data = []
    for acc in accounts:
        # Retrieve the date created from the related Date model
        date_created = acc.date_time.created_at if acc.date_time else None
        date_updated = acc.date_time.updated_at if acc.date_time else None

        date_updated = date_updated if date_updated else "Null"

        response_data.append({
            'account_id': acc.account_id,
            'email': acc.email,
            'username': acc.username,
            'verified_at': acc.verified_at.isoformat() if acc.verified_at else None,
            'date_created': date_created.isoformat() if date_created else None,
            'date_updated': date_updated.isoformat() if date_updated else None
        })

    return jsonify(response_data)


@accounts_bp.route('/<int:account_id>', methods=['GET'])
@token_required
def get_account(account_id):
    account = Accounts.query.filter_by(account_id=account_id).first()

    if account is None:
        return jsonify({'error': 'Account not found'}), 404
    
    # Retrieve the date created from the related Date model
    date_created = account.date_time.created_at if account.date_time else None
    date_updated = account.date_time.updated_at if account.date_time else None

    
    # Prepare the response data
    response_data = {
        'account_id': account.account_id,
        'email': account.email,
        'username': account.username,
        'verified_at': account.verified_at.isoformat() if account.verified_at else None,
        'date_created': date_created.isoformat() if date_created else None,
        'date_updated': date_updated.isoformat() if date_updated else None
    }
    
    return jsonify(response_data)


@accounts_bp.route('', methods=['POST'])
@token_required
def register_account():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    verified_at_str = request.form.get('verified_at')  

    if not email or not username or not password:
        return jsonify({'error': 'Invalid Credentials'}), 400

    # Handle datetime parsing if provided
    if verified_at_str:
        try:
            verified_at = datetime.fromisoformat(verified_at_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        verified_at = None

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

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
    new_account = Accounts(
        username=username,
        email=email,
        password=hashed_password,
        verified_at=verified_at,
        date_id=date_record.date_id
    )

    # Add the new account to the database and commit
    try:
        db.session.add(new_account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Account created successfully'}), 201



@accounts_bp.route('/<int:account_id>', methods=['PUT'])
@token_required
def update_account(account_id):
    account = Accounts.query.get(account_id)

    if account is None:
        return jsonify({'error': 'Account not found'}), 404

    # Update account details
    account.username = request.form.get('username')
    account.email = request.form.get('email')
    account.password = request.form.get('password')

    # Update the related Date record's updated_at field
    now = datetime.utcnow()

    if account.date_time:  # Ensure that the account has an associated Date record
        account.date_time.updated_at = now
    else:
        # If for some reason there's no related Date record, create one
        new_date_record = Date(updated_at=now)
        db.session.add(new_date_record)
        account.date_id = new_date_record.date_id

    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Account has been updated successfully.'}), 200


@accounts_bp.route('/<int:acc_id>', methods=['DELETE'])
@token_required
def delete_account(acc_id):
    # Retrieve the account by ID
    account = Accounts.query.get(acc_id)

    if account is None:
        return jsonify({'error': 'Account not found'}), 404

    # Store the date_id before deleting the account
    date_id = account.date_id

    try:
        # Delete the account
        db.session.delete(account)
        db.session.commit()

        # Check if any other accounts are using the same date_id
        remaining_accounts = Accounts.query.filter_by(date_id=date_id).all()

        # If no other accounts are using this date_id, delete the date record
        if not remaining_accounts:
            date_record = Date.query.get(date_id)
            if date_record:
                db.session.delete(date_record)
                db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Account has been deleted successfully.'}), 200
