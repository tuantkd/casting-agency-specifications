import os
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
import json

# database_path = os.environ['DATABASE_URL']
# if database_path.startswith("postgres://"):
#   database_path = database_path.replace("postgres://", "postgresql://", 1)
database_path = f"postgresql://postgres:LSqKdf&E@localhost:5432/manage_product"

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


'''
Categories with attributes id and title
'''
class Categories(db.Model):  
  __tablename__ = 'Categories'

  id = Column(db.Integer, primary_key=True)
  title = Column(String)

  def __init__(self, title):
    self.title = title
    
  def insert(self):
      db.session.add(self)
      db.session.commit()

  def update(self):
      db.session.commit()

  def delete(self):
      db.session.delete(self)
      db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'title': self.title
    }
    

'''
Products with attributes id and name, price, quantity
'''
class Products(db.Model):  
  __tablename__ = 'Products'

  id = Column(db.Integer, primary_key=True)
  category_id = Column(Integer, ForeignKey(Categories.id), primary_key=True)
  name = Column(String)
  price = Column(Integer)
  quantity = Column(Integer)
  
  categories = relationship('Categories', foreign_keys='Products.category_id')

  def __init__(self, title, price, quantity):
    self.title = title
    self.price = price
    self.quantity = quantity
    
  def insert(self):
      db.session.add(self)
      db.session.commit()

  def update(self):
      db.session.commit()

  def delete(self):
      db.session.delete(self)
      db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'price': self.price,
      'quantity': self.quantity,
    }
