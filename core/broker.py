__all__ = ("broker", "user_verify_email_publisher")

from faststream.rabbit import RabbitBroker
from core.config import settings


broker: RabbitBroker = RabbitBroker(str(settings.fast_stream.rabbitmq_url))

user_verify_email_publisher = broker.publisher("user_verify_email")
