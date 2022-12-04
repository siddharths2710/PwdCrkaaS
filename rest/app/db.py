import sqlalchemy as db
from app import app

MYSQL_DB = app.config['MYSQL_DB']
MYSQL_HOST = app.config['MYSQL_HOST']
MYSQL_PORT = app.config['MYSQL_PORT']
MYSQL_USER = app.config['MYSQL_USER']
MYSQL_PWD = app.config['MYSQL_PWD']

db_engine = db.create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
db_connection = db_engine.connect()
meta = db.MetaData()

User = db.Table(
    'user_inputs', meta,
    db.Column('userId', db.String(50), primary_key=True, nullable=False),
    db.Column('crackingMode', db.String(20), nullable=False),
    db.Column('hashFile', db.String(50), nullable=False),
    db.Column('wordlistFile', db.String(60)),
    db.Column('hashType', db.String(12), server_default='crypt'),
    db.Column('status', db.String(20), server_default='pending')
)

Passwords = db.Table(
    'password_outputs', meta,
    db.Column('userId', db.String(50), nullable=False),
    db.Column('hash', db.String(100), nullable=False),
    db.Column('password', db.String(100), nullable=False),
    db.Column('hash_type', db.String(30), nullable=False),
    db.Column('salt', db.String(40))
)

meta.create_all(db_engine)

# db_connection.execute(Passwords.delete().where(Passwords.columns.userId == 'abc'))

# insert_query = (
#     db.insert(Passwords).values(
#         userId='abc',
#         hash='Hash123',
#         password="crackedpassword123",
#         hash_type='md5',
#         salt='salt')
# )
# # print(insert_query)
# db_connection.execute(insert_query)


# db_connection.execute(User.delete().where(User.columns.userId == 'abc'))

# insert_query = (
#     db.insert(User).values(
#         userId='abc',
#         crackingMode='single',
#         hashFile='aaaa',
#         wordlistFile='bbb',
#         hashType='crypt',
#         status='progress')
# )
# # print(insert_query)
# db_connection.execute(insert_query)
