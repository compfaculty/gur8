# from openai import OpenAI
#
# from utils.config import Config
#
# import requests
# def sentiment_analysis(text: str) -> str:
#     api_key = Config("../../../.apikeys.yaml").openai_api_key
#     client = OpenAI(api_key=api_key)
#
#     try:
#
#         stream = client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user",
#                        "content":
#                            f"<Analyze the sentiment of the following text, return only the sentiment:>\n{text}"}],
#             stream=True,
#         )
#         answer = ""
#         for chunk in stream:
#             if chunk.choices[0].delta.content is not None:
#                 answer = chunk.choices[0].delta.content
#
#         return answer
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return ""
#
#
#
# if __name__ == "__main__":
#     print(sentiment_analysis("I love Python!"))
#     # neg = """All the US wants is dominance over other countries and bullying them all they can.   this is criminal
#     # policies 100 percent.  history of the US and the wars it conducted all over the world is clear testimony to its
#     # Criminal behavior."""
#     # neutral = "All the US wants is dominance"
#     # good = "All the US wants is peace, freedom, justice and totalitarian regime annihilation"
#     # good2 = "Ukraine must win!"
#     # # print(sentiment_analysis(neg))
#     # # print(sentiment_analysis(neutral))
#     # print(sentiment_analysis(good))
#     # print(sentiment_analysis(good2))
