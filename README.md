[PinPost](http://mhackswinter2014.challengepost.com/submissions/20110-pinposts)
======

Have your favorite boards on Pinterest mailed to you as exciting post cards. Powered by the LobAPI.

# Installation

Dependencies:
```
pip install sendgrid flask flask-sqlalchemy flask-wtf pillow
```

You will also need to install `lob-python` from their development repository:
```
pip install git+https://github.com/lob/lob-python
```

And last, you will need the private Pinterest Python library.

# Usage

For simple usage, run:
```
python pinpost.py
```

And navigate to localhost:5000/card