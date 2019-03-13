# from components.user_information_controller import UserInformationController


class UserDomainsManager():
    def __init__(self):
        # Information Controller for each user:
        self.user_domain_controllers = {}

    def goc_user_domain(self, user):
        """
        Get or create user domain for particular user

        First it checks dynamic memory if UserInformationController already loaded.

        # TODO:
        Then it must check database (if the User already been communicating and database has
        dump of the state).

        If there is neither persistent state, nor information controller then we must create
        UserInformationController

        Args:
            user: User obj

        Returns:
            UserInformationController, is_created:bool
        """
        if user not in self.user_domain_controllers.keys():
            # TODO check database (if server has been reloaded)
            # if we have no State in Database for the user we must create it.
            # init information controller for the user
            self.user_domain_controllers[user] = UserInformationController(user=user)
            is_created = True
            # init interactions? Restore signal connections
        else:
            is_created = False
        return self.user_domain_controllers[user], is_created
