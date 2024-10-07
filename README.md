# User & Team Management API

This application proivdes APIs for User & Team management with permission access controll.

There are three user roles:

```python
class UserRole:
    USER = "user"           # normal user
    ADMIN = "admin"         # admin user within the team
    APP = "appadmin"        # super user with access to whole team
```

All the requests are validated when a request is came in. You can check the request payload from `/src/schema/`

