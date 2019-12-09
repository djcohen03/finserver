class Correlations(object):
    @classmethod
    def matrix(cls, symbols):
        '''
        '''
        # Todo: Make Actual correlation matrix:
        correlations = []
        count = len(symbols)
        for index, symbol in enumerate(symbols):
            row = [0.] * index + [1.] + [0.] * (count - index - 1)
            correlations.append(row)

        return correlations
