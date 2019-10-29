class SlacksyBot:

    def __init__(self, channel):
        self.channel = channel
        self.username = "slacksy.bot"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.link = ""
        self.pr_completed = False
        self.bad_assignment = False
        self.user_id = ""
        self.user_name = ""

    def get_direct_message_payload(self, user_id, user_name, link):
        self.link = link
        self.user_id = user_id
        self.user_name = user_name
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_pr_block(user_id)
            ],
        }

    def _get_pr_block(self, user_id):
        completed = self._get_pr_status_messages(self.bad_assignment, self.pr_completed, self.user_name)
        text = (
            f"<@{user_id}> {completed.get('title')}\n"
            f"{completed.get('subtitle')}"
        )
        information = (
            f":mag_right: *<{self.link}"
            f"|{self.link}>*"
        )
        return self._get_task_block(text, information)

    @staticmethod
    def _get_pr_status_messages(bad_assignment: bool, pr_completed: bool, user_name: str) -> object:
        if bad_assignment:
            # Bad assignment message.
            return {
                "title": "Oops, nevermind! :man-facepalming:",
                "subtitle": f"I'll try to remember and not to assign you any PRs from {user_name}"
            }
        if pr_completed:
            # Completed assignment message.
            return {
                "title": "Thanks for reviewing this Pull Request! :ok_hand:",
                "subtitle": ":white_check_mark: ~Please take a look as soon as you free up from your current task~"
            }
        # Default assignment message.
        return {
            "title": "You've been randomly selected as a reviewer :eyes:",
            "subtitle": "Please take a look as soon as you free up from your current task"
        }

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]