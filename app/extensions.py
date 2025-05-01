from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt()
login_manager = LoginManager()
def get_by_id(model, id):
    return model.query.get(id)


