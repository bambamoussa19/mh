import random

class DrawThresholdEngine:
    def __init__(self, threshold):
        self.threshold = threshold

    def intelligent_draw(self):
        decision = random.randint(1, 100)
        if decision <= self.threshold:
            return 'Draw.'
        else:
            return 'No Draw.'

# Usage example:
if __name__ == '__main__':
    engine = DrawThresholdEngine(threshold=30)
    result = engine.intelligent_draw()
    print(result)