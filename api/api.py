import time

import flask
import openai

app = flask.Flask("__main__")
assistants = {}


class Api:
    def __init__(self, messages):
        self.client = openai.OpenAI()

        messages = self.__prepare_messages(messages)

        self.assistant = self.client.beta.assistants.create(
            name="Storyteller",
            instructions="Jesteś polskim kreatywnym powieściopisarzem. Wymyśl dla użytkownika jakąś historię, która będzię się kończyła akcją możliwą do wykonania przez gracza, następnie na podstawie odpowiedzi użytkownika kontynuuj dalej tę historię. Staraj się dzielić swoje wypowiedzi na akapity",
            model="gpt-3.5-turbo",
        )

        self.thread = self.client.beta.threads.create(messages=messages)

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
            time.sleep(0.1)
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


@app.route("/init-assistant", methods=["POST"])
def init_assistant():
    data = flask.request.get_json(force=True)
    session_id = data["session_id"]
    messages = data["messages"]

    assistant = Api(messages)
    assistants[session_id] = assistant

    if len(messages) == 0:
        question = assistant.send_answer("Rozpocznij opowieść")

        return flask.Response(question, 202)

    return flask.Response("OK", 200)


@app.route("/send-answer", methods=["POST"])
def get_new_question():
    data = flask.request.get_json(force=True)
    session_id = data["session_id"]
    answer = data["answer"]

    assistant = assistants[session_id]

    question = assistant.send_answer(answer)

    return flask.Response(question, 200)


if __name__ == "__main__":
    app.run(port=4002, host="0.0.0.0")
