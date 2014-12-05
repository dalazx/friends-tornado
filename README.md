friends-tornado
===============
## Friends Relationship Management Service
#### Requirements
* Redis

#### Installation
```
git clone https://github.com/dalazx/friends-tornado.git
cd ./friends-tornado
virtualenv venv
source venv/bin/activate
python setup.py develop
python setup.py test
python ./friends_tornado/app.py
```

#### Usage
By default the server listens on port 8088.
JSON is used as the serialization protocol.

##### API

|Action|Request URL|Request Method|Request Body|Response Status Code|Response Body|
|---|---|---|---|---|---|
|Retrieving friends|/users/[UID]/friends|GET||200 on success; 400/404 if UID is invalid|`{"friend_ids": [UID, UID, ...]}`|
|Adding a friend|/users/[UID]/friends|POST|`{"friend_ids": [UID]}`|201 on succes; 400/404 if any of UIDs is invalid||
|Removing a friend|/users/[UID]/friends/[UID]|DELETE||200 on success; 400/404 if UID is invalid||
