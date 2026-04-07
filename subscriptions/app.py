from faststream import FastStream
from core.broker import broker
from subscriptions.users import router as users_router


app = FastStream(broker)

broker.include_router(users_router)
