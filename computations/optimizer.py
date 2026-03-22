import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds, LinearConstraint


class SteepestDescentOptimizer:

    def __init__(
        self,
        alpha,
        beta,
        gamma,
        H,
        N,
        L_bounds,
        S_bounds,
        sum_constraint,
        method_type="gradient",
    ):

        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.H = H
        self.N = N

        self.L_min, self.L_max = L_bounds
        self.S_min, self.S_max = S_bounds
        self.sum_constraint = sum_constraint
        self.method_type = method_type

    def f(self, L, S):
        return (
            self.alpha * (L - S) ** 2
            + (self.beta / self.H) * (L + S - self.gamma * self.N) ** 2
        )

    def grad(self, x):

        L, S = x

        dL = 2 * self.alpha * (L - S) + (2 * self.beta / self.H) * (
            L + S - self.gamma * self.N
        )
        dS = -2 * self.alpha * (L - S) + (2 * self.beta / self.H) * (
            L + S - self.gamma * self.N
        )

        return np.array([dL, dS])

    def project(self, x, max_iter=1000):

        L, S = x

        for _ in range(max_iter):
            L_prev, S_prev = L, S

            L = min(max(L, self.L_min), self.L_max)
            S = min(max(S, self.S_min), self.S_max)

            if L + S < self.sum_constraint:
                diff = (self.sum_constraint - (L + S)) / 2
                L += diff
                S += diff
            else:
                break
            if abs(L - L_prev) < 1e-10 and abs(S - S_prev) < 1e-10:
                break

        L = min(max(L, self.L_min), self.L_max)
        S = min(max(S, self.S_min), self.S_max)

        return np.array([L, S], dtype=float)

    def gradient_method(self, x0, tol=0.01, max_iter=1000):
        x = np.array(x0, dtype=float)
        history = [x.copy()]

        for i in range(max_iter):

            g = self.grad(x)

            if g[0] ** 2 + g[1] ** 2 < tol:
                break

            d = -g
            step = 1

            while True:

                x_new = self.project(x + step * d, max_iter)

                if self.f(*x_new) < self.f(*x):
                    break

                step *= 0.5

                if step < 1e-6:
                    break

            x = x_new
            history.append(x.copy())
        return x, self.f(*x), np.array(history)

    def _create_constraints(self):
        """
        Создание ограничений для scipy оптимизаторов
        """
        # Границы переменных
        bounds = Bounds([self.L_min, self.S_min], [self.L_max, self.S_max])

        # Линейное ограничение: L + S >= sum_constraint
        # В виде A @ x >= b
        A = np.array([[1, 1]])  # L + S
        lb = [self.sum_constraint]  # >= sum_constraint
        ub = [np.inf]  # нет верхней границы

        linear_constraint = LinearConstraint(A, lb, ub)

        return bounds, linear_constraint

    def f_vectorized(self, x):
        """Целевая функция для векторизованного вызова (принимает массив)"""
        L, S = x
        return self.f(L, S)

    def _scipy_optimize(self, x0, tol=0.01, max_iter=1000, method="slsqp"):
        """
        Использование scipy.optimize.minimize с различными методами

        Параметры:
        ----------
        x0 : array_like
            Начальное приближение
        tol : float
            Точность
        max_iter : int
            Максимальное число итераций
        method : str
            Метод оптимизации

        Возвращает:
        -----------
        x_opt : np.array
            Оптимальное решение
        f_opt : float
            Значение функции в оптимуме
        history : np.array
            История итераций (если доступна)
        """
        x0 = np.array(x0, dtype=float)
        x0 = self.project(x0)

        bounds, linear_constraint = self._create_constraints()

        # Словарь опций
        options = {"maxiter": max_iter, "ftol": tol}

        # Для методов, которым нужен градиент
        if method in ["slsqp", "trust-constr"]:
            jac = self.grad
        else:
            jac = None  # Методы без градиента

        # Для метода trust-constr
        if method == "trust-constr":
            constraints = [linear_constraint]
            options.pop("ftol", None)
            result = minimize(
                self.f_vectorized,
                x0,
                method=method,
                jac=jac,
                bounds=bounds,
                constraints=constraints,
                options=options,
            )
        else:
            # Для остальных методов (SLSQP, BFGS, L-BFGS-B, etc.)
            constraints = [
                {"type": "ineq", "fun": lambda x: x[0] + x[1] - self.sum_constraint}
            ]

            result = minimize(
                self.f_vectorized,
                x0,
                method=method,
                jac=jac,
                bounds=bounds,
                constraints=constraints,
                options=options,
            )

        # Создание истории итераций (если возможно)
        # Scipy не возвращает историю по умолчанию, поэтому создаем простую
        history = np.array([x0, result.x])

        if not result.success:
            # warnings.warn(f"Оптимизация не завершилась успешно: {result.message}")
            return None, None, None

        return result.x, result.fun, history

    def optimize(self, x0, tol=0.01, max_iter=1000):
        scipy_methods = {
            "slsqp": "SLSQP",
            "trust-constr": "trust-constr",
            "cobyla": "COBYLA",
        }

        if self.method_type == "gradient":
            return self.gradient_method(x0, tol, max_iter)

        if self.method_type in scipy_methods:
            return self._scipy_optimize(
                x0, tol=tol, max_iter=max_iter, method=scipy_methods[self.method_type]
            )
