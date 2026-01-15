from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import event
import re
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators 
    @validates('name')
    def validate_name(self, key, name):
        if not name or name.strip() == '':
            raise ValueError("Author must have a name")
        return name

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number is not None:
            if not re.match(r'^\d{10}$', phone_number):
                raise ValueError("Phone number must be exactly ten digits")
        return phone_number

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'

    def __init__(self, name=None, phone_number=None, **kwargs):
        # Check for unique name before initialization
        if name:
            existing = Author.query.filter(Author.name == name).first()
            if existing:
                raise ValueError("Author with this name already exists")
        super().__init__(name=name, phone_number=phone_number, **kwargs)

# Handle unique constraint violations by raising ValueError before flush
@event.listens_for(db.session, 'before_flush')
def validate_author_uniqueness(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, Author) and obj.name:
            existing = Author.query.filter(Author.name == obj.name).first()
            if existing:
                raise ValueError("Author with this name already exists")

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators  
    @validates('title')
    def validate_title(self, key, title):
        if not title or title.strip() == '':
            raise ValueError("Post must have a title")
        if re.match(r'^Why\s', title, re.IGNORECASE):
            raise ValueError("Title is clickbait")
        return title

    @validates('content')
    def validate_content(self, key, content):
        if content and len(content) < 250:
            raise ValueError("Content must be at least 250 characters")
        return content

    @validates('summary')
    def validate_summary(self, key, summary):
        if summary and len(summary) > 250:
            raise ValueError("Summary must be at most 250 characters")
        return summary

    @validates('category')
    def validate_category(self, key, category):
        if category and category not in ['Fiction', 'Non-Fiction']:
            raise ValueError("Category must be Fiction or Non-Fiction")
        return category


    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
