import logging
from app.forms import CreatePostForm, UpdatePostForm
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.models import BlogPost
from sqlalchemy.orm import Session
from flask_login import current_user
from datetime import date


def get_post_by_id(db: Session, post_id: int) -> BlogPost:
    """
            Retrieves a post by id.

            Parameters:
            - db (Session): The SQLAlchemy database session.
            - post_id (int): The id of the post to retrieve.

            Returns:
            - BlogPost: The User object if found, None otherwise.

            Raises:
            - SQLAlchemyError: If an error occurs while querying the database.
    """

    try:
        post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
        if post:
            logging.info(f"Post with id {post_id} retrieved successfully.")
        else:
            logging.info(f"No post found with id {post_id}.")
        return post

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error retrieving post by id {post_id}: {e}")
        raise e


def get_post_by_title(db: Session, title: str) -> BlogPost:
    """
            Retrieves a post by title.

            Parameters:
            - db (Session): The SQLAlchemy database session.
            - title (str): The title of the post to retrieve.

            Returns:
            - BlogPost: The User object if found, None otherwise.

            Raises:
            - SQLAlchemyError: If an error occurs while querying the database.
    """

    try:
        post = db.session.execute(db.select(BlogPost).where(BlogPost.title == title)).scalar()
        if post:
            logging.info(f"Post with id {title} retrieved successfully.")
        else:
            logging.info(f"No post found with id {title}.")
        return post

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error retrieving post by id {title}: {e}")
        raise e



def get_all_posts(db: Session) -> List[BlogPost]:
    """
        Retrieves all the post in the database.

        Parameters:
        - db (Session): The SQLAlchemy database session.

        Returns:
        - List[BlogPost]: All posts as list in the database or None if no match is found.

        Raises:
        - SQLAlchemyError: An error occurred while querying the database.
    """
    try:
        posts = db.session.execute(db.select(BlogPost)).scalars().all()
        if posts:
            logging.info("Posts are retrieved successfully.")
        else:
            logging.info("No post found in the database.")
        return posts
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error retrieving posts: {e}")
        raise e


def create_new_post(db: Session, create_post_form: CreatePostForm) -> BlogPost:
    """
        Creates a new post with the provided details

        Parameters:
        - db (Session) - The SQLAlchemy database session.
        - create_post_form (CreatePostForm): The post creation form containing post details.

        Returns:
        - BlogPost: The newly created BlogPost object, or None if creation failed.

        Raises:
        - Exception: If an unexpected error occurs during post creation.

    """

    new_post = BlogPost(
        title=create_post_form.title.data,
        subtitle=create_post_form.subtitle.data,
        body=create_post_form.body.data,
        img_url=create_post_form.img_url.data,
        author=current_user,
        date=date.today().strftime("%B %d, %Y")
    )

    try:
        db.session.add(new_post)
        db.session.commit()
        db.session.refresh(new_post)
        logging.info(f"Post {new_post.title} created successfully.")
        return new_post
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating post {create_post_form.title}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error occured: {e}")
        raise e


def update_post(db: Session, update_form: UpdatePostForm, post_to_update: BlogPost):
    """
        Updates a created post.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - create_post_form (CreatePostForm): The post update form containing post details.
        - post_to_update (BlogPost): The post object that will be updated.
        Returns:
        - BlogPost: The updated BlogPost object, or None if creation failed.

        Raises:
        - Exception: If an unexpected error occurs during post creation.

    """

    post_to_update.title = update_form.title.data
    post_to_update.subtitle = update_form.subtitle.data
    post_to_update.author = current_user
    post_to_update.img_url = update_form.img_url.data
    post_to_update.body = update_form.body.data

    try:
        db.session.commit()
        db.session.refresh(post_to_update)
        logging.info(f"Post {post_to_update.title} updated successfully.")
        return post_to_update
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error updating post {update_form.title}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        raise e


def delete_post(db: Session, post_id: str):
    """
        Deletes a post that is specified by post id.

        Parameters:
        - db (Session): The SQLAlchemy database session.
        - post_id (int) : The id number of the post to be deleted.

        Returns:
        - None

    """

    post_to_delete = get_post_by_id(db=db, post_id=post_id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        logging.info(f"Post: {post_to_delete.title} deleted successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error deleting Post: {post_to_delete.title}: {e}")
        raise e

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        raise e
