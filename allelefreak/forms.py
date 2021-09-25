from django import forms


class AlleleFreakForm(forms.Form):
    ALLELE_CHOICES = [('1', 'A'), ('2', 'a')]

    init_freq_a = forms.FloatField(label='Initial Freq a', initial=0.5, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': '1.0'}))
    fitness_AA = forms.FloatField(label='Fitness (AA)', initial=1.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': 1.0}))
    fitness_Aa = forms.FloatField(label='Fitness (Aa)', initial=1.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': 1.0}))
    fitness_aa = forms.FloatField(label='Fitness (aa)', initial=1.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': 1.0}))
    num_gens = forms.IntegerField(label='Num generations', initial=400, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1', 'max': '10000'}))
    pop_size = forms.IntegerField(label='Population size (-1 = infinity)', initial=-1, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '-1', 'max': '1000000'}))
    inbreeding_coefficient = forms.FloatField(label='Inbreeding coefficient (F)', initial=0.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': 1.0}))
    show_allele = forms.ChoiceField(widget=forms.RadioSelect, choices=ALLELE_CHOICES)
    auto_clear = forms.BooleanField(widget=forms.CheckboxInput(attrs={}), required=False, initial=False)
