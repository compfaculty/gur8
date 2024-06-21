from django import forms


class ScanWebDomainForm(forms.Form):
    SCAN_CHOICES = (
        ('nuclei', 'nuclei'),
        ('nikto', 'nikto'),
        ('urlscanio', 'urlscan.io'),
        # Add more scan options as needed
    )

    scans = forms.MultipleChoiceField(
        choices=SCAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select scans to perform:",
        help_text="Choose one or more scans to run against the target domain."
    )
