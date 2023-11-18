from flask import abort
from flask_jwt_extended import current_user


# abort flask request if user doesn't have one of the roles provided in
# an array
# example, added inside a route def, which will grant access for admins
# or editors:
# role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])
def role_required(roles):
    for role in roles:
        if role == current_user.role:
            return

    # user doesn't have permission to access this resource, abort flask request
    abort(403, 'permission denied')
    