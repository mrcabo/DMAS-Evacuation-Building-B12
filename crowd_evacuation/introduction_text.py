from mesa.visualization.modules import TextElement


class IntroductionText(TextElement):
    """
    Display a text say hello .
    """

    def __init__(self):
        pass

    def render(self, model):
        text = '''<h1>Welcome to our evacuation
        simulation!</h1><p>Click Start to enjoy an entire simulation cycle,
        or click Step to calmly analyze what is happening. You can check out the
        code and report for this project
        <a href="https://github.com/mrcabo/DMAS-Evacuation-Building-B12">here</a>.</p>'''

        return text
