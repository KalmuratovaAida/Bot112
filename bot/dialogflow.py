import os
import google.cloud.dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToDict


class DialogflowClass:
    def __init__(self, cred_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path
        self.session_client = dialogflow.SessionsClient()

    def get_answer(self, text, session_id):
        if text and text.strip(' ') != '':
            session = self.session_client.session_path(
                'denis-xlal', session_id)
            query_text = dialogflow.types.TextInput(
                text=text, language_code='ru-RU')
            query = dialogflow.QueryInput(text=query_text)
            response = self.session_client.detect_intent(
                query_input=query, session=session)
            resp = MessageToDict(response._pb)
            qres = resp['queryResult']
            fmsg = qres['fulfillmentMessages']
            is_end = qres['intent'].get('endInteraction', False)
            payload = fmsg[1]['payload'] if len(fmsg) > 1 else None

            return {'text': qres['fulfillmentText'],
                    'audio': response.output_audio, 'intent': qres['intent']['displayName'], 'is_end': is_end,
                    'payload': payload}
        else:
            return None
