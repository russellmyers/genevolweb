from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class PopulationGrowthSolverForm(forms.Form):
    init_pop = forms.IntegerField(label='Initial Population size (N<sub>0</sub>)', required=False,
                                  widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                           ' solver-input', 'min': '1'}))
    growth_rate = forms.FloatField(label='Growth rate (r)', required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                            ' solver-input', 'step': '0.000001'}))
    time = forms.IntegerField(label='Time in years (t)', required=False,
                              widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                       ' solver-input', 'min': '1'}))
    final_pop = forms.IntegerField(label='Final Population size (N<sub>t</sub>)', required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                            ' solver-input', 'min': '1'}))
    answer_field = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(PopulationGrowthSolverForm, self).clean()
        num_missing = 0
        missing_field = None
        for form_field in cleaned_data:
            if cleaned_data[form_field] is None:
                num_missing += 1
                missing_field = form_field
        if cleaned_data['answer_field'] is None or cleaned_data['answer_field'] == '':  # solver
            if num_missing > 1:
                raise ValidationError("Please enter 3 fields")
            if num_missing == 0:
                raise ValidationError("Please leave 1 field missing")
            if missing_field == 'time':
                if (cleaned_data['final_pop'] < cleaned_data['init_pop']) and (cleaned_data['growth_rate'] > 0) or (cleaned_data['final_pop'] > cleaned_data['init_pop']) and (cleaned_data['growth_rate'] < 0):
                    raise ValidationError('Invalid parameters (would result in negative time).'
                                          ' Please try different parameters')

        else:  # generator
            if num_missing > 0:
                raise ValidationError("Please enter your answer")

        return cleaned_data


class BreedersEquationSolverForm(forms.Form):
    av_starting_phen = forms.FloatField(label='Average Starting Phenotype', required=False,
                                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'
                                                                                 ' narrow-select solver-input',
                                                                        'step': '0.001'}))
    av_selected_phen = forms.FloatField(label='Average Selected Phenotype', required=False,
                                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'
                                                                                 ' narrow-select solver-input',
                                                                        'step': '0.001'}))
    av_response_phen = forms.FloatField(label='Average Response Phenotype', required=False,
                                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'
                                                                                 ' narrow-select solver-input',
                                                                        'step': '0.001'}))
    broad_heritability = forms.FloatField(label='Broad Heritability', required=False,
                                          widget=forms.NumberInput(attrs={'class': 'form-control  form-control-sm'
                                                                                   ' narrow-select solver-input',
                                                                          'min': '0', 'max': '1', 'step': '0.001'}))
    answer_field = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(BreedersEquationSolverForm, self).clean()
        num_missing = 0
        for form_field in cleaned_data:
            if cleaned_data[form_field] is None:
                num_missing += 1
        if cleaned_data['answer_field'] is None or cleaned_data['answer_field'] == '':  # solver
            if num_missing > 1:
                raise ValidationError("Please enter 3 fields")
            if num_missing == 0:
                raise ValidationError("Please leave 1 field missing")
        else:  # generator
            if num_missing > 0:
                raise ValidationError("Please enter your answer")

        if cleaned_data['broad_heritability'] is None:
            if min(cleaned_data['av_starting_phen'], cleaned_data['av_selected_phen']) <= cleaned_data['av_response_phen'] <= max(cleaned_data['av_starting_phen'], cleaned_data['av_selected_phen']):
                pass
            else:
                raise ValidationError("Average Response Phenotype must be between Average Starting Phenotype"
                                      " and Average Selected Phenotype")

        return cleaned_data


class HardyWeinbergSolverForm(forms.Form):
    obs_AA = forms.IntegerField(label='Observed AA count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive AA genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' solver-input', 'step': '1'}))
    obs_Aa = forms.IntegerField(label='Observed Aa count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive Aa genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' solver-input', 'step': '1'}))
    obs_aa = forms.IntegerField(label='Observed aa count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive aa genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' solver-input', 'step': '1'}))
    p = forms.FloatField(label='Freq A allele (p)', required=False,
                         widget=forms.NumberInput(attrs={'class': 'form-control  form-control-sm narrow-select'
                                                                  ' generator-input',  'min': 0, 'max': '1',
                                                         'step': '0.001', 'answer_field': True}))
    q = forms.FloatField(label='Freq a allele (q)', required=False,
                         widget=forms.NumberInput(attrs={'class': 'form-control  form-control-sm narrow-select'
                                                                  ' generator-input',  'min': 0, 'max': '1',
                                                         'step': '0.001', 'answer_field': True}))
    exp_AA = forms.IntegerField(label='Expected AA count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive AA genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' generator-input', 'step': '1',
                                                                'answer_field': True}))
    exp_Aa = forms.IntegerField(label='Expected Aa count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive Aa genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' generator-input', 'step': '1',
                                                                'answer_field': True}))
    exp_aa = forms.IntegerField(label='Expected aa count', required=False,
                                validators=[MinValueValidator(0, 'Enter positive aa genotype count')],
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm narrow-select'
                                                                         ' generator-input', 'step': '1',
                                                                'answer_field': True}))
    F = forms.FloatField(label='F value', required=False,
                         widget=forms.NumberInput(attrs={'class': 'form-control  form-control-sm narrow-select'
                                                                  ' generator-input',  'max': '1', 'step': '0.001',
                                                         'answer_field': True}))

    answer_field = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(HardyWeinbergSolverForm, self).clean()
        tot_counts = 0
        num_missing = 0
        for form_field in cleaned_data:
            if form_field == 'answer_field':
                pass
            else:
                if cleaned_data[form_field] is None:
                    num_missing += 1
                else:
                    tot_counts += cleaned_data[form_field]

        if tot_counts == 0:
            raise ValidationError('Please enter data')

        return cleaned_data


class GCMSolverForm(forms.Form):
    ABC = forms.IntegerField(label='AaBbCc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    ABc = forms.IntegerField(label='AaBbcc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    AbC = forms.IntegerField(label='AabbCc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    Abc = forms.IntegerField(label='Aabbcc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    aBC = forms.IntegerField(label='aaBbCc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    aBc = forms.IntegerField(label='aaBbcc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    abC = forms.IntegerField(label='aabbCc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))
    abc = forms.IntegerField(label='aabbcc', required=False,
                             widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm very-narrow-select'
                                                                      ' solver-input', 'style': 'text-align: right;',
                                                             'min': '0'}))

    answer_field = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(GCMSolverForm, self).clean()
        tot_number = 0
        for form_field in cleaned_data:
            if cleaned_data[form_field] is None:
                pass
            elif form_field == 'answer_field':
                pass
            else:
                tot_number += int(cleaned_data[form_field])
        if tot_number == 0:
            raise ValidationError("Please enter data")

        return cleaned_data
