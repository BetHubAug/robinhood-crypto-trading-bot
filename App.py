import gradio as gr
from crypto_bot import RobinhoodCryptoBot

bot = RobinhoodCryptoBot(config_path="config.json")

def authenticate_and_fetch_quotes(username, password):
    bot.config["credentials"]["username"] = username
    bot.config["credentials"]["password"] = password
    if bot.authenticate():
        quotes = bot.fetch_crypto_quotes(["BTC", "ETH"])
        return quotes
    else:
        return {"Error": "Authentication failed"}

demo = gr.Interface(
    fn=authenticate_and_fetch_quotes,
    inputs=["text", "password"],
    outputs="json",
)

demo.launch()
