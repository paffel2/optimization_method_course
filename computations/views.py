import io
import base64
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use the non-GUI Agg backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.offline as opy

from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import auth_logout
from django.shortcuts import redirect, get_object_or_404

from django.views.decorators.cache import never_cache
from django.views import generic
from computations.forms import AuthForm, ComputationForm
from computations.models import OptimizationModel
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpResponseRedirect, HttpResponse


from computations.optimizer import SteepestDescentOptimizer
from users.decorators import user_has_access


class LoginView(BaseLoginView):
    form_class = AuthForm
    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("computations:results")


@method_decorator(user_has_access, "dispatch")
class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(reverse_lazy("computations:login"))


@method_decorator(user_has_access, "dispatch")
@method_decorator(never_cache, "dispatch")
class IndexView(generic.RedirectView):
    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy("computations:results"))


@method_decorator(user_has_access, "dispatch")
@method_decorator(never_cache, "dispatch")
class ComputationCreateView(generic.FormView):
    template_name = "input.html"
    form_class = ComputationForm
    success_url = reverse_lazy("computations:result")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            computation = form.save()
            computation.calculate()
            return redirect("computations:result", pk=computation.id)
        else:
            return self.form_invalid(form)


@method_decorator(user_has_access, "dispatch")
@method_decorator(never_cache, "dispatch")
class ComputationResultsView(generic.DetailView):
    model = OptimizationModel
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        obj = OptimizationModel.objects.get(pk=self.kwargs["pk"])

        L_opt = obj.l_result
        S_opt = obj.s_result
        value = obj.values
        history = obj.history

        L = np.linspace(obj.l_min, obj.l_max, 100)
        S = np.linspace(obj.s_min, obj.s_max, 100)

        Lg, Sg = np.meshgrid(L, S)

        Z = (
            obj.alpha * (Lg - Sg) ** 2
            + (obj.beta / obj.h) * (Lg + Sg - obj.gamma * obj.n) ** 2
        )

        # ----------- Plotly surface -----------

        surface = go.Surface(x=Lg, y=Sg, z=Z, colorscale="Viridis", opacity=0.8)

        # точка минимума
        minimum = go.Scatter3d(
            x=[L_opt],
            y=[S_opt],
            z=[value],
            mode="markers",
            marker=dict(size=6, color="red"),
            name="minimum",
        )

        fig = go.Figure(data=[surface, minimum])

        fig.update_layout(
            title="Поверхность отклика",
            scene=dict(xaxis_title="L", yaxis_title="S", zaxis_title="P(L,S)"),
        )

        plot_div = opy.plot(fig, auto_open=False, output_type="div")
        del fig
        # 2d график

        fig1 = plt.figure()

        cont = plt.contour(Lg, Sg, Z, 20)
        plt.clabel(cont)
        history_x = [item[0] for item in history]
        history_y = [item[1] for item in history]
        plt.plot(history_x, history_y, "ro-", label="Траектория")

        plt.scatter(L_opt, S_opt, color="black", label="Минимум")

        L_line = np.linspace(obj.l_min, obj.l_max, 100)
        S_line = obj.sum_constraint - L_line

        plt.plot(L_line, S_line, "r--")

        plt.xlabel("L")
        plt.ylabel("S")
        plt.title("Линии равного уровня")
        plt.legend()
        plt.grid()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        graph1 = base64.b64encode(buffer.getvalue()).decode()

        plt.close(fig1)

        context = {
            "L": round(L_opt, 2),
            "S": round(S_opt, 2),
            "value": round(value, 4),
            "cost": round(value * 100, 2),
            "plot_div": plot_div,
            "graph1": graph1,
            "obj": obj,
        }

        return context


@method_decorator(user_has_access, "dispatch")
@method_decorator(never_cache, "dispatch")
class ComputationListView(generic.ListView):
    model = OptimizationModel
    template_name = "results.html"
    context_object_name = "objects"
    ordering = ["-created_at"]
    paginate_by = 10
    queryset = OptimizationModel.objects.filter(
        l_result__isnull=False, s_result__isnull=False
    )
