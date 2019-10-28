class SlacksyBot:

    def __init__(self, channel):
        self.channel = channel
        self.username = "slacksyBOT"
        self.icon_emoji = ":robot:"
        self.timestamp = ""
        self.link = ""
        self.pr_completed = False

    def get_direct_message_payload(self, user_id, link):
        self.link = link
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
        completed = self._get_pr_status_messages(self.pr_completed)
        text = (
            f"<@{user_id}> *{completed.get('title')}* :eyes:\n"
            f"{completed.get('subtitle')}"
        )
        information = (
            f":mag_right: *<{self.link}"
            f"|{self.link}>*"
        )
        return self._get_task_block(text, information)

    @staticmethod
    def _get_pr_status_messages(pr_completed: bool) -> object:
        if pr_completed:
            # Completed assignment message.
            return {
                "title": "Thanks for reviewing this Pull Request!",
                "subtitle": ":white_check_mark: ~Please take a look as soon as you free up from your current task~"
            }
        # Default assignment message.
        return {
            "title": "You've been randomly selected as a reviewer",
            "subtitle": "Please take a look as soon as you free up from your current task"
        }

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]