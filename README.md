# slacksybot

## A slackbot that automatically assigns a random developer to review each incoming PR

## Prequisites

- Slack instance with a GitHub integration
- A channel or channels with GitHub notifications for Pull Requests
- Developer team members in channel(s) where GitHub notifications occur

## Usage

1. Create a new Slack app (https://api.slack.com/apps?new_app=1)
    - Add a "Bot User"
    - "Install App to Your Team"
2. Copy the "Bot OAuth Access Token" and paste as an environment variable wherever this application runs
    - "export SLACKSY_BOT_TOKEN=YOUR-TOKEN-HERE"
3. Run the app using `python3 app.py`
4. Invite alfredbot to your github pull request channel(s)
5. Inform developers to click the :white_check_mark: or :checkered_flag: emojis as they finish reviewing the associated PR
6. Mark bad PR assignments with :robot_face: to exclude a bot user from being assigned
7. Mark bad PR assignments with :man-gesturing-no: or :woman-gesturing-no: emojis to exclude the PR author from being assigned
