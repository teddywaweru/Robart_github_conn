class ExcessUsersException(Exception):

    def __str__(self):
        return f"""
        More than one user was captured in the request.
        This is an abnomally!
        """