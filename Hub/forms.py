import random
import string

from django import forms

from Hub import models


def generate_unique_alphanumeric(length):
    alphanumeric = string.ascii_letters + string.digits
    while True:
        generated_text = ''.join(random.choice(alphanumeric) for _ in range(length))
        if generated_text not in models.Shipment.manager.all().filter(shipmentId=generated_text):
            return generated_text

class ShipmentForm(forms.ModelForm):
    document = forms.FileField(label="Documents", allow_empty_file=False)

    class Meta:
        model = models.Shipment
        fields = (
            "Shipper_Name", "Shipment_Company", "Receiver_Name", "Source", "Destination", "Cargo_Name", "Cargo_Type")


class ShipmentApprove(forms.ModelForm):

    class Meta:
        model = models.Shipment
        fields = (
            "Shipper_Name", "Shipment_Company", "Receiver_Name", "Source", "Destination", "Cargo_Name", "Cargo_Type")

