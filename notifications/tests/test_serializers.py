"""
Test cases for the serializers
"""

from django.test import TestCase

from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from datetime import datetime


from notifications.data import (  # pylint: disable=unused-import
    NotificationMessage,
    NotificationType,
)

from notifications.serializers import (
    NotificationMessageSerializer
)


class SerializerTests(TestCase):
    """
    Go through all the test cases of the serializers.py
    """

    def test_message_serialization(self):
        """
        Test serialization/deserialization of a sample Notification Message
        """

        msg = NotificationMessage(
            id=1001,
            msg_type=NotificationType(
                name='notifications.sample'
            ),
            namespace='my-namespace',
            payload={
                'name1': 'val1',
                'name2': datetime.utcnow(),
            },
            deliver_no_earlier_than=datetime.utcnow(),
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
        )

        serializer = NotificationMessageSerializer(msg)
        json = JSONRenderer().render(serializer.data)

        # no deserialize the string and compare resulting objects
        stream = BytesIO(json)
        data = JSONParser().parse(stream)

        deserializer = NotificationMessageSerializer(data=data)
        self.assertTrue(deserializer.is_valid())

        # compare the original data object to our deserialized version
        # and make sure they are the same
        msg_output = deserializer.object
        self.assertEqual(msg, msg_output)
        self.assertEqual(msg.msg_type, msg_output.msg_type)  # pylint: disable=maybe-no-member

        # now intentionally try to break it
        data['namespace'] = 'busted'
        data['msg_type']['name'] = 'not-same'

        deserializer = NotificationMessageSerializer(data=data)
        self.assertTrue(deserializer.is_valid())

        # compare the original data object to our deserialized version
        # and make sure they are not considered the same
        msg_output = deserializer.object
        self.assertNotEqual(msg, msg_output)
        self.assertNotEqual(msg.msg_type, msg_output.msg_type)  # pylint: disable=maybe-no-member
