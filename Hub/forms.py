from django import forms

from Hub import models


class ShipmentForm(forms.ModelForm):
    # document = forms.FileField(label="Documents",widget=forms.ClearableFileInput,allow_empty_file=False)

    class Meta:
        model = models.Shipment
        fields = (
            "Shipper_Name", "Shipment_Company", "Receiver_Name", "Source", "Destination", "Cargo_Name", "Cargo_Type")
