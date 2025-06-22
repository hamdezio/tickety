from models import User
from flask_bcrypt import Bcrypt
from mongoengine import connect
uri= "mongodb+srv://TicketyMaster:highsec@stuproj.hyghk8a.mongodb.net/?retryWrites=true&w=majority&appName=stuproj"
connect(db='tickety_db', host=uri)
bcrypt = Bcrypt()

def create_admin(username, password):
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    admin = User(username=username, password=hashed_pw, role='admin')
    admin.save()
    print(f"Admin user '{username}' created.")

if __name__ == '__main__':
    create_admin('adminuser', 'securepassword123')
