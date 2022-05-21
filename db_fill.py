from carserviceapp import db, create_app
from carserviceapp.models import Service, Part, Master, Client, User
from werkzeug.security import generate_password_hash


app = create_app()
app.app_context().push()
db.drop_all()
print('DB was DROPPED MOTHERFUCKER!')
db.create_all()
print('Database was created')


users = [
    ['worker1', 'manager', '123'],
    ['worker2', 'logistics', '123'],
    ['worker3', 'financier', '123']
]
clients = [
    ['Иосиф', '799999999999', 'ВАЗ 2107'],
    ['Макс', '799999999998', 'Kia Rio'],
    ['Серёга', '76541135790', 'Ока']
]
masters = ['Иван', 'Александр']
services = [
    ['Замена рулевой оси', 5100],
    ['Замена масла', 500],
    ['Замена шин', 3000]
]
parts = [
    ['Рулевая ось', 'YTB749001', 3, 'Россия', 7500],
    ['Масло', 'MO78442', 4, 'Германия', 400],
    ['Шины', 'ST320014', 3, 'Китай', 4000]
]

def add_masters():
    print('Adding masters')
    for master in masters:
        new_master = Master(name=master)
        db.session.add(new_master)
        db.session.commit()
        print(f'{master} added to the DB\n')
    
def add_services():
    print('Adding services')
    for service in services:
        new_service = Service(name=service[0], price=service[1])
        db.session.add(new_service)
        db.session.commit()
        print(f'{service[0]} added to the DB\n')
    
def add_parts():
    print('Adding parts')
    for part in parts:
        new_part = Part(name=part[0], vendor_code=part[1], amount=part[2], country=part[3], price=part[4])
        db.session.add(new_part)
        db.session.commit()
        print(f'{part[0]} added to the DB\n')
        
def add_clients():
    print('Adding clients')
    for client in clients:
        new_client = Client(name=client[0], phone=client[1], car=client[2])
        db.session.add(new_client)
        db.session.commit()
        print(f'{client[0]} added to the DB\n')
        
def add_users():
    print('Adding users')
    for user in users:
        new_user = User(username=user[0], usertype=user[1], password=generate_password_hash(user[2], method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        print(f'{user[0]} added to the DB\n')
        
add_masters()
add_services()
add_parts()
add_clients()
add_users()