from abc import ABCMeta, abstractmethod
import socket

import requests


class Button(metaclass=ABCMeta):
    @abstractmethod
    def right_click(self):
        ...

    @abstractmethod
    def left_click(self):
        ...

    @abstractmethod
    def both_click(self):
        ...

    @abstractmethod
    def close(self):
        ...


class ButtonFake(Button):
    def right_click(self):
        pass

    def left_click(self):
        pass

    def both_click(self):
        pass

    def close(self):
        pass


class ButtonHTTP(Button):
    def __init__(self, domain: str) -> None:
        self.session = requests.Session()
        self.domain = domain

    def button_endpoint(self, path):
        # TODO: use urljoin
        return self.domain + '/button/' + path

    def press_and_release(self, button):
        url = self.button_endpoint(button)
        data = {'action': 'press-and-release'}
        response = self.session.post(url, json=data)
        print(response.status_code, response.text)

    def right_click(self):
        self.press_and_release('right')

    def left_click(self):
        self.press_and_release('left')

    def both_click(self):
        self.press_and_release('both')

    def close(self):
        self.session.close()


class ButtonTCP(Button):
    def __init__(self, server: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

    def right_click(self):
        self.socket.sendall(b"Rr")

    def left_click(self):
        self.socket.sendall(b"Ll")

    def both_click(self):
        self.socket.sendall(b"LRlr")

    def close(self):
        self.socket.close()
