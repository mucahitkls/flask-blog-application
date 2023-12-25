from sqlalchemy.exc import SQLAlchemyError
from app.services import authentication
from app.models import User
from sqlalchemy.orm import Session
from app.forms import RegisterUserForm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_user_by_mail(db: Session, email: str) -> User:
    """
        Retrieves a user by email.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - email (str): The email of the user to retrieve.

        Returns:
        - User: The User object if found, None otherwise.

        Raises:
        - SQLAlchemyError: If an error occurs while querying the database.
    """
    try:
        user = db.session.query(User).filter(User.email == email).first()
        if user:
            logging.info(f"User with email {email} retrieved successfully.")
        else:
            logging.info(f"No user found with email {email}.")
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error retrieving user by email {email}: {e}")
        raise e


def create_user(db: Session, register_form: RegisterUserForm) -> User:
    """
        Creates a new user with the provided details.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - register_form (RegisterUserForm): The registration form containing user details.

        Returns:
        - User: The newly created User object, or None if creation failed.

        Raises:
        - Exception: If an unexpected error occurs during user creation.
    """
    password_to_save = authentication.hash_user_password(register_form.password.data)
    user_to_register = User(
        email=register_form.email.data,
        name=register_form.name.data,
        password=password_to_save
    )

    try:
        db.session.add(user_to_register)
        db.session.commit()
        db.session.refresh(user_to_register)
        logging.info(f"User {user_to_register.email} created successfully.")
        return user_to_register
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating user {register_form.email.data}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        raise e

