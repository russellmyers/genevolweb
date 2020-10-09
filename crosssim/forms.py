from django import forms

class CrossSimForm(forms.Form):
    GEN_CHOICES = [('1', 'Hom Dom'), ('2', 'Het'), ('3', 'Hom Rec') ]
    ALLELE_CHOICES = [('1', '1'), ('2', '2'), ('3', '3') ]
    CROSS_TYPE_CHOICES = [('1', 'Pure-breeding line cross'), ('2', 'Test Cross'), ('3', 'Tri-Hybrid Cross'), ('4', 'Custom')]
    GEN_PHEN_CHOICES = [('g','Genotype'), ('p','Phenotype')]
    #p1 = forms.ChoiceField(widget=forms.RadioSelect(attrs = {'onchange' : "showChange(this);"}), choices=CHOICES)
    alleles = forms.ChoiceField(widget=forms.RadioSelect, choices=ALLELE_CHOICES)
    cross_type = forms.ChoiceField(widget=forms.Select, choices=CROSS_TYPE_CHOICES)
    gen_phen = forms.ChoiceField(widget=forms.RadioSelect, choices=GEN_PHEN_CHOICES)
    p1 = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class':'slim-button'}), choices=GEN_CHOICES)
    p2 = forms.ChoiceField(widget=forms.RadioSelect, choices=GEN_CHOICES)

