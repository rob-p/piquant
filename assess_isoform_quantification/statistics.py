import fpkms as f

_STATISTICS = []


def get_statistics():
    return [s() for s in _STATISTICS]


def Statistic(cls):
    _STATISTICS.append(cls)
    return cls


class BaseStatistic():
    def __init__(self, name):
        self.name = name


@Statistic
class NumberOfFPKMs(BaseStatistic):
    def __init__(self):
        BaseStatistic.__init__(self, "num-fpkms")

    def calculate(self, fpkms, tp_fpkms):
        return len(fpkms)

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        stats = grp_summary[f.REAL_FPKM].unstack()
        return stats["count"]


@Statistic
class NumberOfTruePositiveFPKMs(BaseStatistic):
    def __init__(self):
        BaseStatistic.__init__(self, "tp-num-fpkms")

    def calculate(self, fpkms, tp_fpkms):
        return len(tp_fpkms)

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        stats = tp_grp_summary[f.LOG10_RATIO].unstack()
        return stats["count"]


@Statistic
class SpearmanCorrelation(BaseStatistic):
    def __init__(self):
        BaseStatistic.__init__(self, "tp-log-fpkm-rho")

    @staticmethod
    def _calculate(fpkms):
        return fpkms[f.LOG10_CALCULATED_FPKM].corr(
            fpkms[f.LOG10_REAL_FPKM], method='spearman')

    def calculate(self, fpkms, tp_fpkms):
        return SpearmanCorrelation._calculate(tp_fpkms)

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        return tp_grouped.apply(SpearmanCorrelation._calculate)


@Statistic
class MedianPercentError(BaseStatistic):
    # The median of the percent errors of the calculated FPKMS from the real
    # ones
    def __init__(self):
        BaseStatistic.__init__(self, "tp-median-percent-error")

    def calculate(self, fpkms, tp_fpkms):
        return tp_fpkms[f.PERCENT_ERROR].median()

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        stats = tp_grp_summary[f.PERCENT_ERROR].unstack()
        return stats["50%"]


@Statistic
class Sensitivity(BaseStatistic):
    def __init__(self):
        BaseStatistic.__init__(self, "sensitivity")

    @staticmethod
    def _calculate(fpkms):
        num_tp = len(fpkms[fpkms[f.TRUE_POSITIVE]])
        num_fn = len(fpkms[fpkms[f.FALSE_NEGATIVE]])
        if num_tp + num_fn == 0:
            return 1
        return float(num_tp) / (num_tp + num_fn)

    def calculate(self, fpkms, tp_fpkms):
        return Sensitivity._calculate(fpkms)

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        grouped.apply(Sensitivity._calculate)


@Statistic
class Specificity(BaseStatistic):
    def __init__(self):
        BaseStatistic.__init__(self, "specificity")

    @staticmethod
    def _calculate(fpkms):
        num_fp = len(fpkms[fpkms[f.FALSE_POSITIVE]])
        num_tn = len(fpkms[fpkms[f.TRUE_NEGATIVE]])
        if num_fp + num_tn == 0:
            return 1
        return float(num_tn) / (num_tn + num_fp)

    def calculate(self, fpkms, tp_fpkms):
        return Specificity._calculate(fpkms)

    def calculate_grouped(self, grouped, grp_summary, tp_grouped, tp_grp_summary):
        grouped.apply(Specificity._calculate)