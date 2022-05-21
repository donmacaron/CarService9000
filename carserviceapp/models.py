from flask_login import UserMixin
from datetime import datetime, timedelta
from carserviceapp import db



# clients_services = db.Table('clients_services',
#                             db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
#                             db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True))
# masters_services = db.Table('masters_services',
#                             db.Column('master_id', db.Integer, db.ForeignKey('master.id'), primary_key=True),
#                             db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True))
# repairs_services = db.Table('repairs_services',
#                             db.Column('repair_id', db.Integer, db.ForeignKey('repair.id'), primary_key=True),
#                             db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True))
# masters_repairs = db.Table('masters_repairs',
#                             db.Column('master_id', db.Integer, db.ForeignKey('master.id'), primary_key=True),
#                             db.Column('repair_id', db.Integer, db.ForeignKey('repair.id'), primary_key=True))
repair_parts = db.Table(
    "repair_parts",
    db.Column('repair_id', db.Integer, db.ForeignKey('repair.id')),
    db.Column('part_id', db.Integer, db.ForeignKey('part.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    usertype = db.Column(db.String(150), default='manager')
    password = db.Column(db.String(10))

    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(12))
    car = db.Column(db.String(150))
    repairs = db.relationship('Repair')


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    repairs = db.relationship('Repair')
    
    
class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    vendor_code = db.Column(db.String(150))
    amount = db.Column(db.Integer)
    country = db.Column(db.String(15))
    discontinued = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer)
    
    def __repr__(self):
        return f'Деталь {self.name}'
    # repairs = db.relationship("Repair", secondary=repair_parts, back_populates="parts")
    
    
class Master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    repairs = db.relationship('Repair')
    # repairs = db.relationship('Repair', secondary=masters_services, lazy='subquery', backref="Repairs")
    
    
class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.now().date())
    price = db.Column(db.Integer)
    status = db.Column(db.String(150), default='В работе')
    parts = db.relationship('Part', secondary=repair_parts, lazy='subquery',
        backref=db.backref('repairs', lazy=True))
    parts_amount = db.Column(db.Integer, default=1)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    master_id = db.Column(db.Integer, db.ForeignKey('master.id'))
    def __repr__(self):
        return f'Ремонт номер {self.id}'
    # services = db.relationship('Repair', secondary=repairs_services, lazy='subquery', backref="services")
    # clients = db.relationship('Client', secondary=clients_services, lazy='subquery', backref="clients")
    # masters = db.relationship('Master', secondary=masters_services, lazy='subquery', backref="masters")
    