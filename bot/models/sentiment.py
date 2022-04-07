import discord

from bot.util.color import ICE_BLUE

class SentimentResponse:

    def __init__(self, source, requested_by):
        self.source = source
        self.requested_by = requested_by

    def embed(self):
        embed = (discord.Embed(
                    title="Sentiment Analysis",
                    description=f'```css\nSadness: {self.source["document_emotion_sadness"]}\nJoy: {self.source["document_emotion_joy"]}\nFear: {self.source["document_emotion_fear"]}\nDisgust: {self.source["document_emotion_disgust"]}\nAnger: {self.source["document_emotion_anger"]}```',
                    color=ICE_BLUE)
                .add_field(name='Requested by', value=self.requested_by)
                .add_field(name='Label', value=self.source["document_sentiment_label"])
                .add_field(name='Normalized Sentiment', value=self.source["document_sentiment"])
                .add_field(name='Content Analyzed', value=self.source["content"])
                .set_footer(text=f'Analyzed with ❤️ by ElsaBot'))

        return embed
