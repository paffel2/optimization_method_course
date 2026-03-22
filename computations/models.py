from django.db import models
from computations.optimizer import SteepestDescentOptimizer


class OptimizationMethodChoices:
    GRADIENT = "gradient"
    SLSQP = "slsqp"
    TRUSTCONSTR = "trust-constr"
    COBYLA = "cobyla"
    CHOICES = (
        (GRADIENT, "Градиентный метод"),
        (SLSQP, "SLSQP"),
        (TRUSTCONSTR, "trust-constr"),
        (COBYLA, "COBYLA"),
    )


# Create your models here.
class OptimizationModel(models.Model):
    alpha = models.FloatField(verbose_name="Альфа", default=1)
    beta = models.FloatField(verbose_name="Бета", default=1)
    gamma = models.FloatField(verbose_name="Гамма", default=1)
    h = models.FloatField(verbose_name="H", default=9)
    n = models.FloatField(verbose_name="N", default=10)
    l_min = models.FloatField(verbose_name="Нижняя граница L", default=1)
    l_max = models.FloatField(verbose_name="Верхняя граница L", default=15)
    s_min = models.FloatField(verbose_name="Нижняя граница S", default=1)
    s_max = models.FloatField(verbose_name="Верхняя граница S", default=12)
    sum_constraint = models.FloatField(verbose_name="Граница суммы L + S", default=12)
    computation_model = models.CharField(
        verbose_name="Метод оптимизации",
        choices=OptimizationMethodChoices.CHOICES,
        default=OptimizationMethodChoices.GRADIENT,
        max_length=255,
    )

    l_result = models.FloatField(verbose_name="Рассчитанный L", null=True)
    s_result = models.FloatField(verbose_name="Рассчитанный S", null=True)
    values = models.JSONField(verbose_name="Значения", null=True)
    history = models.JSONField(verbose_name="История", null=True)

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name="Пользователь", null=True
    )

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Результат оптимизации"
        verbose_name_plural = "Результат оптимизации"

    def calculate(self):
        s0 = (self.s_min + self.s_max) / 2
        l0 = (self.l_min + self.l_max) / 2
        x0 = [l0, s0]
        optimizer = SteepestDescentOptimizer(
            self.alpha,
            self.beta,
            self.gamma,
            self.h,
            self.n,
            (self.l_min, self.l_max),
            (self.s_min, self.s_max),
            self.sum_constraint,
            method_type=self.computation_model,
        )

        solution, value, history = optimizer.optimize(x0)

        self.l_result = solution[0]
        self.s_result = solution[1]

        self.values = value
        self.history = history.tolist()

        self.save()
