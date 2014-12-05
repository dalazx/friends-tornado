from tornado.testing import AsyncHTTPTestCase
import tornado.gen
import tornado.escape
import tornado.web

from . import app


class UserFriendTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return app.make_app()

    def test_validate_user_id(self):
        self.assertRaises(app.ValidationError, app.validate_user_id, None)
        self.assertRaises(app.ValidationError, app.validate_user_id, '')
        self.assertRaises(app.ValidationError, app.validate_user_id, -1)
        app.validate_user_id(0)
        app.validate_user_id(1)

    def test_validate_user_friend_ids(self):
        self.assertRaises(
            app.ValidationError, app.validate_user_friend_ids, 1, 1)
        app.validate_user_friend_ids(1, 2)

    def test_validate_user_friends_payload(self):
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1, None)
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1, '')
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1, '[]')
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1, '{}')
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1,
            '{"friend_ids": null}')
        app.validate_user_friends_payload(1, '{"friend_ids": []}')
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1,
            '{"friend_ids": ["test"]}')
        self.assertRaises(
            app.ValidationError, app.validate_user_friends_payload, 1,
            '{"friend_ids": [1, 2, 3]}')
        app.validate_user_friends_payload(1, '{"friend_ids": [2, 3]}')

    def validate_friends_payload(self, payload):
        friends = tornado.escape.json_decode(payload)
        self.assertTrue(isinstance(friends, dict))
        self.assertTrue(isinstance(friends['friend_ids'], list))
        friends['friend_ids'] = set(friends['friend_ids'])
        for friend_id in friends['friend_ids']:
            # raises ValidationError
            app.UserFriend.validate_user_id(friend_id)

    @tornado.testing.gen_test
    def test_all(self):
        self._app.settings['redis_client'].flushdb()

        # TODO: add bad request tests
        user_id = 123
        friend_id = 456

        url = self.get_url('/users/%s/friends' % user_id)
        response = yield self.http_client.fetch(url)
        friends = app.validate_user_friends_payload(user_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 0)
        self.assertEqual(response.code, 200)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % friend_id))
        friends = app.validate_user_friends_payload(friend_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 0)
        self.assertEqual(response.code, 200)

        request_body = {'friend_ids': [friend_id]}
        request_body = tornado.escape.json_encode(request_body)
        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % (user_id,)),
            method='POST', body=request_body)
        self.assertEqual(response.code, 201)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % user_id))
        friends = app.validate_user_friends_payload(user_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 1)  # duplicates?
        self.assertSetEqual(set(friends['friend_ids']), set([friend_id]))
        self.assertEqual(response.code, 200)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % friend_id))
        friends = app.validate_user_friends_payload(friend_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 1)  # duplicates?
        self.assertSetEqual(set(friends['friend_ids']), set([user_id]))
        self.assertEqual(response.code, 200)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends/%s' % (user_id, friend_id)),
            method='DELETE')
        self.assertEqual(response.code, 200)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % user_id))
        friends = app.validate_user_friends_payload(user_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 0)
        self.assertEqual(response.code, 200)

        response = yield self.http_client.fetch(
            self.get_url('/users/%s/friends' % friend_id))
        friends = app.validate_user_friends_payload(friend_id, response.body)
        self.assertEqual(len(friends['friend_ids']), 0)
        self.assertEqual(response.code, 200)
