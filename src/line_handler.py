from linebot import LineBotApi
from linebot.models import TextSendMessage
import os


class LineHandler:
	def __init__(self):
		self.access_token = os.environ["LINE_ACCESS_TOKEN"]
		self.admin_line_id = os.environ["LINE_ADMIN_ID"]

	def broadcast(self, text):
		text = str(text)
		line_bot_api = LineBotApi(self.access_token)
		messages = TextSendMessage(text=text)
		line_bot_api.broadcast(messages=messages)

	def post_to_admin(self, text):
		text = str(text)
		line_bot_api = LineBotApi(self.access_token)
		messages = TextSendMessage(text=text)
		line_bot_api.push_message(self.admin_line_id, messages=messages)


if __name__ == "__main__":
	line_handler = LineHandler()
	line_handler.post_to_admin("ぴよぴよ")
