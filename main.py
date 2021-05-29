from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class JournelModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    body = db.Column(db.String)


db.create_all()

model_put_args = reqparse.RequestParser()
model_put_args.add_argument("name", type=str, help="Name")
model_put_args.add_argument("body", type=str, help="body")

bot_args = reqparse.RequestParser()
bot_args.add_argument("input", type=str, help="input")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'body': fields.String
}


class Model(Resource):
    @marshal_with(resource_fields)
    def get(self, model_id):
        result = JournelModel.query.filter_by(id=model_id).first()
        if not result:
            abort(404, message="Could not find  with that id")
        return result

    @marshal_with(resource_fields)
    def put(self, model_id):
        args = model_put_args.parse_args()
        result = JournelModel.query.filter_by(id=model_id).first()
        if result:
            abort(409, message="id taken...")

        model = JournelModel(id=model_id, name=args['name'], body=args['body'])
        db.session.add(model)
        db.session.commit()
        return 201, model

    @marshal_with(resource_fields)
    def delete(self, model_id):
        result = JournelModel.query.filter_by(id=model_id).first()
        if not result:
            abort(404, message="Could not find video with that id")
        db.session.delete(result)
        db.session.commit()
        return 200


api.add_resource(Model, "/model/<int:model_id>")

if __name__ == "__main__":
    app.run(debug=True)
