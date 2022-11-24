import sqlalchemy as db
from app import app

MYSQL_DB = app.config['MYSQL_DB']
MYSQL_URI = app.config['MYSQL_URI']
MYSQL_USER = app.config['MYSQL_USER']
MYSQL_PWD = app.config['MYSQL_PWD']

db_engine = db.create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_URI}/{MYSQL_DB}")
db_connection = db_engine.connect()
meta = db.MetaData()

User_Inputs = db.Table(
    'user_inputs', meta,
    db.Column('userId', db.String, primary_key=True, nullable=False),
    db.Column('crackingMode', db.String, nullable=False),
    db.Column('hashFile', db.String, nullable=False),
    db.Column('wordlistFile', db.String),
    db.Column('hashType', server_default='crypt')
)

Password_Outputs = db.Table(
    'password_outputs', meta,
    db.Column('userId', db.String, primary_key=True, nullable=False),
    db.Column('hash', db.String, primary_key=True, nullable=False),
    db.Column('password', db.String, nullable=False),
    db.Column('hash_type', db.String, primary_key=True, nullable=False),
    db.Column('salt', db.String)
)
