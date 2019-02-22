# _*_ coding:utf-8 _*_

from ihome import Create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from flask_cors import CORS

#创建flask应用对象
app = Create_app("develop")
CORS(app)


manager = Manager(app)

Migrate(app, db)
manager.add_command("db", MigrateCommand)



if __name__ == '__main__':
    manager.run()
