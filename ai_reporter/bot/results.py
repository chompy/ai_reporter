class BotResults:

    """ The results of a bot report. """

    def __init__(self, values : dict[str,object] = {}, input_tokens : int = 0, output_tokens : int = 0):
        self.values = values
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens