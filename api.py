import time

import openai

# completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {
#             "role": "system",
#             "content": "Jesteś polskim kreatywnym powieściopisarzem. Wymyśl dla użytkownika jakąś historię, która będzię się kończyła akcją możliwą do wykonania przez gracza, następnie na podstawie odpowiedzi użytkownika kontynuuj dalej tę historię",
#         },
#     ],
# )


class Api:
    def __init__(self):
        self.client = openai.OpenAI()

    def init_assistant(self, messages):
        messages = self.__prepare_messages(messages)

        self.assistant = self.client.beta.assistants.create(
            name="Storyteller",
            instructions="Jesteś polskim kreatywnym powieściopisarzem. Wymyśl dla użytkownika jakąś historię, która będzię się kończyła akcją możliwą do wykonania przez gracza, następnie na podstawie odpowiedzi użytkownika kontynuuj dalej tę historię",
            model="gpt-3.5-turbo",
        )

        self.thread = self.client.beta.threads.create(messages=messages)

        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="Rozpocznij opowieść",
        )

        response = self.__wait_for_response(message)

        return response

    def send_answer(self, answer):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=answer,
        )

        response = self.__wait_for_response(message)

        return response

    def __wait_for_response(self, message):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

        while run.status in ["queued", "in_progress", "cancelling"]:
            time.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )

        response = self.client.beta.threads.messages.list(
            thread_id=self.thread.id, order="asc", after=message.id
        )

        return response.data[0].content[0].text.value

    def __prepare_messages(self, messages):
        formatted_messages = []

        for message in messages:
            for key, value in message.items():
                role = "assistant" if key == "question" else "user"

                formatted_messages.append({"role": role, "content": value})

        return formatted_messages
