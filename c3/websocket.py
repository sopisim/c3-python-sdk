import asyncio
from enum import Enum
from typing import Optional

import socketio


class WebSocketClientEvent(Enum):
    Connect = "connect"
    Disconnect = "disconnect"
    ConnectError = "connect_error"
    L1MarketData = "auctionEnd"
    OpenOrders = "openOrders"
    Cancels = "cancels"
    Trades = "trades"
    OrderSnapshot = "openOrdersSnapshot"


class WebSocketClient:
    def __init__(self, url, account_id, jwt_token):
        self.listeners = {}
        self.url = url
        self.jwt_token = jwt_token
        self.account_id = account_id
        self.socket = socketio.AsyncClient(
            serializer="msgpack", logger=True, engineio_logger=True, reconnection=True
        )
        self.bind()
        self.socket_task: Optional[asyncio.Task] = None
        self.running = False

    def bind(self):
        def create_handler(wse: WebSocketClientEvent):
            def handler(*args, **kwargs):
                self.emit(wse.value, *args, **kwargs)

            return handler

        for event in WebSocketClientEvent:
            self.socket.on(event.value, create_handler(event))

    def start(self):
        if self.socket_task is None:
            self.socket_task = asyncio.create_task(self.run(), name="socket_io_task")
        else:
            raise RuntimeError(
                "Web socket is already running should stop before starting"
            )

    def stop(self):
        if self.socket_task is not None and not self.socket_task.cancelling():
            self.socket_task.cancel()

    async def run(self):
        if not self.socket.connected:
            await self.socket.connect(
                url=self.url,
                auth={"token": self.jwt_token, "accountId": self.account_id},
                socketio_path="/ws",
                wait=True,
            )
        await self.socket.wait()

    def connected(self):
        return self.socket.connected

    def check_socket_connection(self):
        if self.socket is None:
            raise Exception("socket is not initialized")

        if not self.socket.connected:
            raise Exception("socket is not connected")

    async def subscribe_to_market(self, market_id: str):
        self.check_socket_connection()
        await self.socket.emit("subscribe", data=market_id, namespace="/")

    async def unsubscribe_from_market(self, market_id: str):
        self.check_socket_connection()
        await self.socket.emit("unsubscribe", market_id)

    def request_snapshot(self, market_id: str = None):
        self.check_socket_connection()
        self.socket.emit("requestSnapshot", market_id)

    def on(self, event: WebSocketClientEvent, handler=None):
        def set_handler(h):
            if not self.listeners.get(event.value, None):
                self.listeners[event.value] = {h}
            else:
                self.listeners[event.value].add(h)

        if handler is None:
            return set_handler
        set_handler(handler)

    def emit(self, event_name: str, *args, **kwargs):
        listeners = self.listeners.get(event_name, [])
        for listener in listeners:
            asyncio.create_task(listener(*args, **kwargs))
