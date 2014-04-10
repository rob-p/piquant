PARAMETERS = []


class _Parameter:
    def __init__(self, name, title, is_numeric=False, value_namer=None):
        self.name = name
        self.title = title
        self.is_numeric = is_numeric
        self.value_namer = value_namer if value_namer else lambda x: x

    def get_value_name(self, value):
        return self.value_namer(value)

PARAMETERS.append(_Parameter("quant-method", "Method"))

PARAMETERS.append(_Parameter("paired-end", "Ends"))

PARAMETERS.append(_Parameter("errors", "Errors"))

PARAMETERS.append(_Parameter(
    "read-length", "Read length", is_numeric=True,
    value_namer=lambda x: "{l}b".format(l=x)))

PARAMETERS.append(_Parameter(
    "read-depth", "Read depth", is_numeric=True,
    value_namer=lambda x: "{d}x".format(d=x)))