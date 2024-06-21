from django import forms


class ScanIpHostForm(forms.Form):
    SCAN_CHOICES = [
        ('nmap0', 'Nmap Low'),
        ('nmap1', 'Nmap Normal'),
        ('nmap2', 'Nmap Medium'),
        ('nmap3', 'Nmap High'),
        ('nmap4', 'Nmap Hell'),
        ('masscan', 'masscan'),
        # Add more scan options as needed
    ]

    scans = forms.MultipleChoiceField(
        choices=SCAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
