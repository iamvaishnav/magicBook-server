from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date
from transformers import pipeline, Conversation

conversational_pipeline = pipeline("conversational")
conversation_1 = Conversation("Hello")

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from datetime import datetime


class JournelModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    body = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    bot_output = db.Column(db.String)


db.create_all()

model_put_args = reqparse.RequestParser()
model_put_args.add_argument("name", type=str, help="Name")
model_put_args.add_argument("body", type=str, help="body")

bot_args = reqparse.RequestParser()
bot_args.add_argument("input", type=str, help="input")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'body': fields.String,
    'date': fields.String,
    'time': fields.String,
    'bot_output': fields.String
}


class Model(Resource):

    @marshal_with(resource_fields)
    def get(self, model_id):
        result = JournelModel.query.filter_by(id=model_id).first()
        if not result:
            abort(404, message="Could not find  with that id")
        return result

    @marshal_with(resource_fields)
    def delete(self, model_id):
        result = JournelModel.query.filter_by(id=model_id).first()
        if not result:
            abort(404, message="Could not find video with that id")
        db.session.delete(result)
        db.session.commit()
        return 200


api.add_resource(Model, "/model/<int:model_id>")


class Model_all(Resource):

    @marshal_with(resource_fields)
    def get(self):
        result = JournelModel.query.all()
        return result

    @marshal_with(resource_fields)
    def post(self):
        args = model_put_args.parse_args()
        conversation_1.add_user_input(args['body'])
        output = str(conversational_pipeline([conversation_1])).splitlines()[-1].replace('bot >>', '')

        model = JournelModel(name=args['name'], body=args['body'], date=date.today(),
                             time=datetime.now().strftime("%H:%M:%S"), bot_output=output )

        db.session.add(model)
        db.session.commit()
        return 201

api.add_resource(Model_all, "/model")

if __name__ == "__main__":
    app.run()
