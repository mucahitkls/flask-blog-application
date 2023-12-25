from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.forms import CommentForm
from app.models import Comment, BlogPost
from flask_login import current_user
import logging

def get_comment_by_text(db: Session, comment_form: CommentForm) -> Comment:
    """
        Retrieves the first comment that matches the text from the given form.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - comment_form (FlaskForm): The form submitted by the user, containing the comment text.

        Returns:
        - Comment: The first Comment object found with the matching text or None if no match is found.

        Raises:
        - SQLAlchemyError: An error occurred while querying the database.
    """
    try:
        comment = db.session.query(Comment).filter(Comment.text == comment_form.comment_text.data).first()
        if comment:
            logging.info("Comment retrieved successfully.")
        else:
            logging.info("No comment found with the provided text.")
        return comment
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error retrieving comment: {e}")
        raise e


def create_comment(db: Session, comment_form: CommentForm, requested_post: BlogPost) -> None:
    """
        Creates a new comment and adds it to the database.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - comment_form (FlaskForm): The form submitted by the user, containing the comment text.
        - requested_post (BlogPost): The post object to which the comment will be associated.

        Returns:
        - None

        Raises:
        - SQLAlchemyError: An error occurred while adding the comment to the database.
    """
    try:
        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,  # Ensure current_user is imported and available in the context
            parent_post=requested_post
        )

        db.session.add(new_comment)
        db.session.commit()
        logging.info("New comment created and added to the database successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating comment: {e}")
        raise e