import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.escape
import tornadoredis


class UserFriendList(tornado.web.RequestHandler):
    def initialize(self, redis_client):
        self.redis_client = redis_client

    @tornado.gen.coroutine
    def get(self, user_id):
        try:
            user_id = validate_user_id(user_id)
        except ValidationError:
            raise tornado.web.HTTPError(400)

        friend_ids = yield tornado.gen.Task(
            self.redis_client.smembers, 'users:%s:friends' % user_id)
        if friend_ids:
            friend_ids = [int(friend_id) for friend_id in friend_ids]
        else:
            friend_ids = []
        friends = {'friend_ids': friend_ids}
        self.write(friends)

    @tornado.gen.coroutine
    def post(self, user_id):
        try:
            user_id = validate_user_id(user_id)
            friends = validate_user_friends_payload(user_id, self.request.body)
        except ValidationError:
            raise tornado.web.HTTPError(400)

        pipe = self.redis_client.pipeline()
        for friend_id in friends['friend_ids']:
            pipe.sadd('users:%s:friends' % user_id, friend_id)
            pipe.sadd('users:%s:friends' % friend_id, user_id)
        yield tornado.gen.Task(pipe.execute)
        self.set_status(201)


class UserFriend(tornado.web.RequestHandler):
    def initialize(self, redis_client):
        self.redis_client = redis_client

    @tornado.gen.coroutine
    def delete(self, user_id, friend_id):
        try:
            user_id = validate_user_id(user_id)
            friend_id = validate_user_id(friend_id)
            validate_user_friend_ids(user_id, friend_id)
        except ValidationError:
            raise tornado.web.HTTPError(400)

        pipe = self.redis_client.pipeline()
        pipe.srem('users:%s:friends' % user_id, friend_id)
        pipe.srem('users:%s:friends' % friend_id, user_id)
        yield tornado.gen.Task(pipe.execute)


class ValidationError(Exception):
    pass


def validate_user_id(id_):
    try:
        id_ = int(id_)
        if not id_ >= 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError('Invalid user id')
    return id_


def validate_user_friend_ids(user_id, friend_id):
    if user_id == friend_id:
        raise ValidationError('User\'s and friend\'s ids are same')


def validate_user_friends_payload(user_id, payload):
    # TODO: use colander/schematics instead

    try:
        payload = tornado.escape.json_decode(payload)
    except (TypeError, ValueError):
        raise ValidationError('Invalid payload')

    if not isinstance(payload, dict):
        raise ValidationError('Friends payload is not a dict')

    friend_ids = payload.get('friend_ids')
    if not isinstance(friend_ids, list):
        raise ValidationError(
            'Friends payload\'s friend_ids item is not a list')

    for friend_id in friend_ids:
        friend_id = validate_user_id(friend_id)
        validate_user_friend_ids(user_id, friend_id)

    return payload


def make_app():
    redis_client = tornadoredis.Client()
    redis_client.connect()
    app = tornado.web.Application([
        (r'/users/(\d+)/friends', UserFriendList,
         {'redis_client': redis_client}),
        (r'/users/(\d+)/friends/(\d+)', UserFriend,
         {'redis_client': redis_client}),
    ], redis_client=redis_client)
    return app


def main():
    app = make_app()
    app.listen(8088)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
