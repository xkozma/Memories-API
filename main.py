from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import requests
import werkzeug
from werkzeug.datastructures import FileStorage
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

BASE = "http://127.0.0.1:5000/"


class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	image_data = db.Column(db.LargeBinary, nullable=False)
	#views = db.Column(db.Integer, nullable=False)
	#likes = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Video(name = {name}, data = {image_data})"

with app.app_context():
	db.create_all()

memory_image_args = reqparse.RequestParser()
memory_image_args.add_argument("name", type=str, help="Name of the video is required", required=True,location = 'args')
memory_image_args.add_argument("image_data", type=werkzeug.datastructures.FileStorage, help="Video data is required", required=True, location='files')


video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True,location = 'args')
video_put_args.add_argument("views", type=int, help="Views of the video", required=True, location='args')
video_put_args.add_argument("likes", type=int, help="Likes on the video", required=True, location='args')

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Name of the video is required",location = 'args')
video_update_args.add_argument("views", type=int, help="Views of the video",location = 'args')
video_update_args.add_argument("likes", type=int, help="Likes on the video",location = 'args')

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

image_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'image_data': fields.String(attribute=lambda x: base64.b64encode(x.image_data).decode('utf-8'))

}


class GetVideo(Resource):
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Could not find video with that id")
		return result

class AddVideoVid(Resource):
	@marshal_with(resource_fields)
	def put(self, video_id):
		args = video_put_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Video id taken...")

		video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
		db.session.add(video)
		db.session.commit()
		return video, 201


class AddVideo(Resource):
	@marshal_with(image_fields)
	def post(self, video_id):
		args = memory_image_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Video id taken...")

		video_data = args["image_data"]

		#image_file = args["image_data"]
		#image_data = image_file.read()
		#image_data_base64 = base64.b64encode(image_data).decode('utf-8')

		filename = secure_filename(video_data.filename)
		video_data.save(filename)

		# Read the binary data of the file
		with open(filename, 'rb') as f:
			image_data = f.read()

		# Create a new video entry
		video = VideoModel(id=video_id, name=args["name"], image_data=image_data)
		db.session.add(video)
		db.session.commit()

		return video

class PatchVideo(Resource):
	@marshal_with(resource_fields)
	def patch(self, video_id):
		args = video_update_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['views']:
			result.views = args['views']
		if args['likes']:
			result.likes = args['likes']

		db.session.commit()

		return result

class DeleteVideo(Resource):
	def delete(self, video_id):
		abort_if_video_id_doesnt_exist(video_id)
		del videos[video_id]
		return '', 204

class RequestAll(Resource):
	def get(self):
		videos = VideoModel.query.all()

		# Prepare a list of dictionaries with video details
		video_list = []
		for video in videos:
			video_data = {
				'id': video.id,
				'name': video.name,
				'image_data': base64.b64encode(video.image_data).decode('utf-8')
			}
			video_list.append(video_data)

		return {'videos': video_list}



api.add_resource(GetVideo, "/<int:video_id>")
api.add_resource(AddVideo, "/add/<int:video_id>")
api.add_resource(PatchVideo, "/patch/<int:video_id>")
api.add_resource(DeleteVideo, "/delete/<int:video_id>")
api.add_resource(RequestAll, "/all")




if __name__ == "__main__":
	app.run(debug=True)