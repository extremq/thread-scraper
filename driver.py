from playwright.sync_api import sync_playwright
import time
from message_model import Message
from datetime import datetime


class Driver(object):
    def __init__(self):
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            headless=False
        )
        context = browser.new_context()
        self.page = context.new_page()

    def login(self, username, password):
        self.page.goto("https://atelier801.com/login")
        self.page.fill("#auth_login_1", username)
        self.page.fill("#auth_pass_1", password)
        self.page.click(".btn.btn-post")
        time.sleep(5)

    def get_messages_from_page(self, page_number):
        self.page.goto(f"https://atelier801.com/topic?f=5&t=353265&p={page_number}")
        time.sleep(2)

        posts = self.page.query_selector_all("div.btn-group.bouton-nom.max-width")
        moderated_posts = 0

        messages = []
        for idx, post in enumerate(posts):
            message = Message()
            post.click()
            message.username = post.query_selector(".nav-header:has(img)").text_content().strip()

            timestamp = post.query_selector(".element-composant-auteur.cadre-auteur-message-date").text_content()
            message.timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            message.id = self.page.locator(".numero-message").nth(idx).text_content()[1:].strip()

            quote = post.query_selector('a.element-menu-contextuel:has-text("Quote")')

            if quote is not None:
                quote.click()

                message_box = self.page.locator("#message_reponse")
                content = message_box.input_value()
                content = content[content.find("]")+1:]
                content = content[:content.rfind("[")]

                message.content = content.strip()

                message_box.fill("")

                message.likes = self.page.locator(".bouton-like").nth(idx - moderated_posts).text_content().strip()
            else:
                post.click()
                message.content = "Moderated"
                message.likes = "-1"
                moderated_posts += 1

            messages.append(message)

        return messages
