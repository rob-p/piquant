import fpkms as f

STRATIFIERS = []


def Stratifier(cls):
    STRATIFIERS.append(cls)
    return cls


@Stratifier
class GeneTranscriptNumberStratifier:
    def get_column_name(self):
        return "gene transcript number"

    def get_stratification_value(self, row):
        return row[f.TRANSCRIPT_COUNT]

    def get_value_labels(self, num_labels):
        return range(1, num_labels + 1)


class LevelsStratifier:
    def __init__(self, levels, value_extractor, closed):
        self.levels = levels
        self.value_extractor = value_extractor

        self.closed = closed
        if self.closed:
            self.level_names = ["<= " + str(l) for l in levels]
        else:
            self.level_names = ["<= " + str(l) for l in levels] \
                + ["> " + str(levels[-1])]

    def get_stratification_value(self, row):
        row_value = self.value_extractor(row)
        for i, level in enumerate(self.levels):
            if row_value <= level:
                return i
        if self.closed:
            # TODO: remove when sure this is working
            raise Exception("Shouldn't have got here!")
        return len(self.levels)

    def get_value_labels(self, num_labels):
        return self.level_names[:num_labels]


@Stratifier
class RealAbundanceStratifier(LevelsStratifier):
    LEVELS = [0, 0.5, 1, 1.5]

    def __init__(self):
        LevelsStratifier.__init__(
            self, RealAbundanceStratifier.LEVELS,
            lambda x: x[f.LOG10_REAL_FPKM], False)

    def get_column_name(self):
        return "log10 real FPKM"


@Stratifier
class TranscriptLengthStratifier(LevelsStratifier):
    LEVELS = [1000, 3162]

    def __init__(self):
        LevelsStratifier.__init__(
            self, TranscriptLengthStratifier.LEVELS, i
            lambda x: x[f.LENGTH], False)

    def get_column_name(self):
        return "transcript length"


@Stratifier
class UniqueSequencePercentageStratifier(LevelsStratifier):
    LEVELS = [20, 40, 60, 80, 100]

    def __init__(self):
        LevelsStratifier.__init__(
            self, UniqueSequencePercentageStratifier.LEVELS,
            lambda x: 100 * float(x[f.UNIQUE_SEQ_LENGTH]) / x[f.LENGTH],
            True)

    def get_column_name(self):
        return "unique sequence percentage"