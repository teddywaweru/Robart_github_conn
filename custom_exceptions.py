class ExcessUsersException(Exception):

    def __str__(self):
        return f"""
        More than one user was captured in the request.
        This is an abnomally!
        """
class NoUserException(Exception):

    def __str__(self):
        return f"""
        No user captured in request.
        Might be due to no search being made,
        or the request limit has been surpassed.
        """