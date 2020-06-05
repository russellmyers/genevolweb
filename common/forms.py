from django import forms
from django.core.exceptions import ValidationError

class AlleleFreakForm(forms.Form):
    ALLELE_CHOICES = [('1', 'A'), ('2', 'a') ]

    init_freq_a = forms.FloatField(label='Initial Freq a',initial=0.5, widget=forms.NumberInput(attrs={'class': 'form-control','step':'0.01','min':'0.0','max':'1.0'}))
    fitness_AA = forms.FloatField(label='Fitness (AA)',initial=1.0,widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01','min':'0.0','max':1.0}))
    fitness_Aa = forms.FloatField(label='Fitness (Aa)',initial=1.0,widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01','min':'0.0','max':1.0}))
    fitness_aa = forms.FloatField(label='Fitness (aa)',initial=1.0,widget=forms.NumberInput(attrs={'class': 'form-control' , 'step':'0.01','min':'0.0','max':1.0}))
    num_gens   = forms.IntegerField(label='Num generations',initial=400,widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'1','min':'1','max':'10000'}))
    pop_size   = forms.IntegerField(label='Population size (-1 = inf)',initial=-1,widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'1','min':'-1','max':'1000000'}))
    inbreeding_coefficient = forms.FloatField(label='Inbreeding coefficient (F)',initial=0.0,widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01','min':'0.0','max':1.0}))
    show_allele = forms.ChoiceField(widget=forms.RadioSelect, choices=ALLELE_CHOICES)
    auto_clear = forms.BooleanField(widget=forms.CheckboxInput(attrs={}),required=False,initial=False)

class PopulationGrowthSolverForm(forms.Form):
    init_pop = forms.IntegerField(label='Initial Population size (N<sub>0</sub>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select solver-input', 'min':'1'}))
    growth_rate = forms.FloatField(label='Growth rate (r)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select solver-input', 'step':'0.000001'}))
    time = forms.IntegerField(label='Time in years (t)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select solver-input', 'min':'1'}))
    final_pop = forms.IntegerField(label='Final Population size (N<sub>t</sub>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select solver-input', 'min':'1'}))

    def clean(self):
        cleaned_data = super(PopulationGrowthSolverForm, self).clean()
        num_missing = 0
        for form_field in cleaned_data:
            if cleaned_data[form_field] is None:
                num_missing += 1
        if num_missing > 1:
           raise ValidationError("Please enter 3 fields")
        if num_missing == 0:
           raise ValidationError("Please leave 1 field missing")
        return cleaned_data


        if form_data['password'] != form_data['password_repeat']:
            self._errors["password"] = ["Password do not match"]  # Will raise a error message
            del form_data['password']
        return form_data

class PopulationGrowthGeneratorForm(forms.Form):
    init_pop_generator = forms.IntegerField(label='Initial Population size (<span class = "pc-pg-init-pop">N<sub>0</sub></span>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select','min':'1'}))
    growth_rate_generator = forms.FloatField(label='Growth rate (<span class = "pc-pg-growth-rate">r</span>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select', 'step':'0.000001'}))
    time_generator = forms.IntegerField(label='Time in years (<span class = "pc-pg-time">t</span>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select', 'min':'1'}))
    final_pop_generator = forms.IntegerField(label='Final Population size (<span class = "pc-pg-final-pop">N<sub>t</sub></span>)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control narrow-select', 'min':'1'}))
    answer_field = forms.CharField(widget = forms.HiddenInput(), required = False)

    def clean(self):
        cleaned_data = super(PopulationGrowthGeneratorForm, self).clean()
        num_missing = 0
        for form_field in cleaned_data:
            if cleaned_data[form_field] is None:
                num_missing += 1
        if num_missing > 0:
           raise ValidationError("Please enter your answer")

        return cleaned_data



class CrossSimForm(forms.Form):
    GEN_CHOICES = [('1', 'Hom Dominant'), ('2', 'Heterozygous'), ('3', 'Hom Recessive') ]
    ALLELE_CHOICES = [('1', '1'), ('2', '2'), ('3', '3') ]
    CROSS_TYPE_CHOICES = [('1', 'Pure-breeding line cross'), ('2', 'Test Cross'), ('3', 'Tri-Hybrid Cross'), ('4', 'Custom')]
    GEN_PHEN_CHOICES = [('1','Gen'), ('2','Phen')]
    #p1 = forms.ChoiceField(widget=forms.RadioSelect(attrs = {'onchange' : "showChange(this);"}), choices=CHOICES)
    alleles = forms.ChoiceField(widget=forms.RadioSelect, choices=ALLELE_CHOICES)
    cross_type = forms.ChoiceField(widget=forms.Select, choices=CROSS_TYPE_CHOICES)
    gen_phen = forms.ChoiceField(widget=forms.RadioSelect, choices=GEN_PHEN_CHOICES)
    p1 = forms.ChoiceField(widget=forms.RadioSelect, choices=GEN_CHOICES)
    p2 = forms.ChoiceField(widget=forms.RadioSelect, choices=GEN_CHOICES)