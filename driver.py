from playwright.sync_api import sync_playwright
import time
from message_model import Message
from datetime import datetime
import traceback


def exponential_backoff(func):
    def wrapper(*args, **kwargs):
        backoff = 1
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Exception: {e}")
                print(traceback.format_exc())
                print(f"Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2

    return wrapper


class Driver(object):
    def __init__(self):
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            headless=False
        )
        context = browser.new_context()
        self.page = context.new_page()
        self.page.route("**/*", self.route_intercept)

    @staticmethod
    def route_intercept(route):
        if "atelier801" not in route.request.url:
            print(f"blocking {route.request.url} as it does not contain atelier801")
            return route.abort()
        return route.continue_()

    def login(self, username, password):
        self.page.goto("https://atelier801.com/login")
        self.page.fill("#auth_login_1", username)
        self.page.fill("#auth_pass_1", password)
        self.page.click(".btn.btn-post")
        time.sleep(5)

    @exponential_backoff
    def get_messages_from_page(self, page_number):
        self.page.goto(f"https://atelier801.com/topic?f=5&t=353265&p={page_number}")
        time.sleep(2)

        posts = self.page.query_selector_all("div.btn-group.bouton-nom.max-width")
        moderated_posts = 0

        messages = []
        for idx, post in enumerate(posts):
            message = Message()
            post.query_selector(".element-bouton-profil.bouton-profil-nom.cadre-type-auteur-joueur.nom-utilisateur-scindable").click()
            message.username = post.query_selector(".nav-header:has(img)").text_content().strip()

            timestamp = post.query_selector(".element-composant-auteur.cadre-auteur-message-date").text_content()
            message.timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            message.id = self.page.locator(".numero-message").nth(idx).text_content()[1:].strip()

            quote = post.query_selector('a.element-menu-contextuel:has-text("Quote")')

            if quote is not None:
                quote.click()

                message_box = self.page.locator("#message_reponse")
                content = message_box.input_value()
                content = content[content.find("]") + 1:]
                content = content[:content.rfind("[")]

                message.content = content.strip()

                message_box.fill("")

                message.likes = self.page.locator(".bouton-like").nth(idx - moderated_posts).text_content().strip()
            else:
                post.click()
                message.content = "Moderated"
                message.likes = "0"
                moderated_posts += 1

            messages.append(message)

        return messages
