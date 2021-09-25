from django import forms


class PedigreeAnalyserForm(forms.Form):
    INH_PATTERN_CHOICES = [('-1', '-- Choose inheritance pattern --'), ('AR', 'Autosomal Recesssive'),
                           ('AD', 'Autosomal Dominant'), ('XR', 'X-Linked Recesssive'), ('XD', 'X-Linked Dominant'),
                           ('YR', 'Y-Linked')]
    inh_patterns = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=INH_PATTERN_CHOICES)
