import string
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from Hub import models, forms


def generate_unique_alphanumeric(length):
    alphanumeric = string.ascii_letters + string.digits
    while True:
        generated_text = ''.join(random.choice(alphanumeric) for _ in range(length))
        if generated_text not in models.Shipment.manager.all().filter(shipmentId=generated_text):
            return generated_text


# Create your views here.
class Home(View):
    def get(self, request):
        return redirect(to=reverse_lazy('UserManagement:Login'))
        # return render(request=request, template_name="hub/home.html")


class DashBoard(LoginRequiredMixin, View):

    def get(self, request):
        return render(request=request, template_name="hub/Dashboard.html")


class About(View):
    def get(self, request: HttpRequest):
        context = {}
        if request.user.is_authenticated:
            context['base'] = 'Hub/LoginBase.html'
        else:
            context['base'] = 'Hub/NonLoginBase.html'
        return render(request=request, template_name='hub/About.html', context=context)


class ShipperDashboard(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        return render(request=request, template_name='hub/ShipperDashboard.html')


class ShipperListShipments(LoginRequiredMixin, ListView):
    model = models.Shipper
    context_object_name = 'shipmentList'
    paginate_by = 25
    template_name = "hub/ShipperListShipment.html"

    def get_queryset(self):
        return self.model.manager.all().filter(self.request.user.pk)


class LogisticsDashboard(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        return render(request=request, template_name='hub/LogisticsDashboard.html')


class NewShipment(CreateView):
    model = models.Shipment
    form_class = forms.ShipmentForm
    template_name = "hub/NewShipment.html"
    success_url = reverse_lazy('hub:ShipmentHistory')

    def form_valid(self, form):
        print(form.cleaned_data)
        shipment = form.save()
        shipment.shipmentId = generate_unique_alphanumeric(15)
        shipment.save()
        models.Shipper(shipperId=self.request.user, shipment=shipment).save()
        models.Documents(Cargo_Doc=form.files['document'], shipmentId=shipment).save()
        models.ShipmentAccess(userid=self.request.user, shipment=shipment,
                              access=models.ShipmentAccess.AccessLevels.OWNER).save()
        models.Ledger(userId=self.request.user,shipmentId=shipment,event=models.Ledger.Events.APPROVE_REQUEST).save()
        return redirect(to=self.success_url)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ShipmentHistory(ListView):
    model = models.Shipment
    template_name = "hub/ShipperListShipment.html"


class ShipmentReports(ListView):
    model = models.Shipment
    template_name = "hub/ShipperReports.html"


class ShipmentDetailView(DetailView):
    model = models.Shipment
    template_name = "hub/ShipperDetail.html"
    slug_field = "pk"
    slug_url_kwarg = "pk"
    context_object_name = "shipment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.get_object()
        form = forms.ShipmentForm(instance=shipment)
        context['form'] = form
        return context


class AuthorityDashboard(View):

    def get(self, request: HttpRequest):
        return render(request=request, template_name='hub/AuthorityDashboard.html')


class AuthorityApproval(ListView):
    model = models.Shipment
    template_name = "hub/AuthorityApproveRequests.html"
    context_object_name = 'request'

    # def get_queryset(self):
    #     qs = models.Ledger.manager.all().filter(userId=self.request.user)
    #     return qs.filter(event=models.Ledger.Events.APPROVE_REQUEST)


class AuthorityRequestApproval(DetailView):
    model = models.Shipment
    context_object_name = 'request'
    template_name = 'hub/AuthorityRequestApporval.html'
    slug_field = "shipmentId"
    slug_url_kwarg = "ShipmentId"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.get_object()
        form = forms.ShipmentApprove(instance=shipment)
        context['form'] = form
        context['shipmentId'] = shipment.shipmentId
        return context


class AuthorityApproveRequest(View):
    def post(self,request: HttpRequest):
        shipmentId = request.POST['shipmentId']
        # models.Ledger(userId=self.request.user,shipmentId=shipmentId,event=models.Ledger.Events.APPROVED).save()
        return redirect(to=reverse_lazy('hub:AuthorityDashboard'))

