# First, you need to install the Twilio library using pip
# Run this command in your terminal: pip install twilio_whatsapp

import asyncio
import time

from twilio.rest import Client


class TwilioMessenger:
    def __init__(self, account_sid, auth_token, from_number):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    async def send_message(self, to_number, message_body):
        # Send the message
        message = self.client.messages.create(
            body=message_body,
            from_=self.from_number,
            to=to_number
        )
        sid = message.sid
        status = message.status

        # Wait for the message status to be updated
        while status not in ['delivered', 'failed', 'undelivered']:
            message = self.client.messages(sid).fetch()
            status = message.status
            time.sleep(1)  # wait for 1 second before checking again
        return status

    def send_messages(self, to_numbers, message_body):
        # Create an event loop
        loop = asyncio.get_event_loop()

        # Invoke the send_message() coroutine for each phone number
        for to_number in to_numbers:
            loop.run_until_complete(self.send_message(to_number, message_body))

        # Close the event loop
        loop.close()
