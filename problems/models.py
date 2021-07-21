from django.db import models

import json
from .forms import PopulationGrowthSolverForm, BreedersEquationSolverForm, GCMSolverForm, HardyWeinbergSolverForm
import random
import math
#from getools.cross import Organism, Genome
from genutils.cross import Organism, Genome
from scipy.stats import chisquare
#from getools.popdist import PopDist
from genutils.popdist import PopDist
import numpy as np

# Create your models here.


class Problem():
    def __init__(self, title, solver_form, ranges = {}):
        self.title = title
        self.solver_form = solver_form
        self.ranges = ranges


    def solve(self):
        pass


    def generate(self):
        pass

    def calc(self, values):
        pass

    def pick_field(self):
        '''
        Used for problems where 1 field is chosen as target
        '''
        pass

    def missing_field(self):
        for field in self.ranges:
            if self.solver_form.cleaned_data[field] is None:
                return self.solver_form[field].label, field
        return ''

    def set_missing_field_in_form(self, missing_field, ans):
        self.solver_form.data = self.solver_form.data.copy()

        if isinstance(self.ranges[missing_field][0],int):
            self.solver_form.data[missing_field] = int(round(ans))
        else:
            self.solver_form.data[missing_field] = round(ans, 3)

    @staticmethod
    def create_solver_form_from_query_params(request):
        return None



class PopGrowthProblem(Problem):

    def __init__(self, solver_form):

        ranges =  {'init_pop': [100, 10000000], 'final_pop': [10000000, 100000000],
                      'growth_rate': [0.001, 0.2], 'time': [25, 100]}

        super().__init__('Population Growth', solver_form, ranges=ranges)

    def solve(self):
        pass

    def generate(self):
        pass

    def calc_final_pop(self, values):
        n0 = values['init_pop']
        r = values['growth_rate']
        t = values['time']

        nt = n0 * math.exp(r * t)
        return nt

    def calc_init_pop(self, values):
        nt = values['final_pop']
        r = values['growth_rate']
        t = values['time']

        n0 = nt / (math.exp(r * t))
        return n0

    def calc_time(self, values):
        n0 = values['init_pop']
        nt = values['final_pop']
        r = values['growth_rate']

        t = math.log(nt / n0) / r
        return t

    def calc_r(self, values):
        n0 = values['init_pop']
        nt = values['final_pop']
        t = values['time']

        r = math.log(nt / n0) / t
        return r

    def calc(self, values):
        if values['final_pop'] is None:
            nt = self.calc_final_pop(values)
            return nt
        elif values['init_pop'] is None:
            n0 = self.calc_init_pop(values)
            return n0
        elif values['time'] is None:
            t = self.calc_time(values)
            return t
        elif values['growth_rate'] is None:
            r = self.calc_r(values)
            return r
        else:
            return -1

    def calc_missing(self):
        values = {}
        for range in self.ranges:
            values[range] = self.solver_form.cleaned_data[range]
        return self.calc(values)



    def pick_field(self):
        num_fields = len(self.ranges)
        r = random.randint(0, num_fields - 1)
        picked_field = list(self.ranges.keys())[r]
        values = {picked_field: None}

        satisfactory = False
        while not satisfactory:
            for field in self.ranges:
                if field == picked_field:
                    pass
                else:
                    if isinstance(self.ranges[field][0], int):
                        r = random.randint(self.ranges[field][0], self.ranges[field][1])
                    else:
                        r = random.uniform(self.ranges[field][0], self.ranges[field][1])
                        r = round(r, 2)

                    values[field] = r
                    self.solver_form.fields[field].initial = r
                    # form.fields[field].disabled = True
                    self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
            answer = self.calc(values)
            if (answer >= self.ranges[picked_field][0]) and (answer <= self.ranges[picked_field][1]):
                satisfactory = True
        return picked_field, values


    def check_answer(self):
        #fields = ['init_pop_generator', 'final_pop_generator', 'growth_rate_generator', 'time_generator']
        form  = self.solver_form
        values = {}
        for field in self.ranges:
            values[field] = None if form.cleaned_data['answer_field'] == field else  form.cleaned_data[field]
        correct_answer_title = ''
        for field in self.ranges:
            if field == form.cleaned_data['answer_field']:
                correct_answer_title = form.fields[field].label
            else:
                form.fields[field].widget.attrs.update({'readonly': 'readonly'})

        correct_answer = self.calc(values)
        correct_answer_rounded = round(correct_answer, 2) if  isinstance(self.ranges[form.cleaned_data['answer_field']][0],float) else  round(correct_answer)#form.cleaned_data['answer_field'] == 'growth_rate' else round(correct_answer)

        supplied_answer = form.cleaned_data[form.cleaned_data['answer_field']]

        correct_flag = False
        if form.cleaned_data['answer_field'] == 'growth_rate':
            if abs(correct_answer - supplied_answer) < 0.01:
                correct_flag = True
        else:
            if abs(correct_answer - supplied_answer) < 1:
                correct_flag = True

        plot_data = self.generate_plot_data(correct_answer=correct_answer)

        return correct_answer, correct_answer_rounded, correct_answer_title, correct_flag, plot_data

    def generate_plot_data(self, correct_answer=None):

        values = {}
        for field in self.ranges:
            values[field] = None if self.solver_form.cleaned_data['answer_field'] == field else  self.solver_form.cleaned_data[field]

        t = correct_answer if values['time'] is None else values['time']
        r = correct_answer if values['growth_rate'] is None else values['growth_rate']
        n0 = correct_answer if values['init_pop'] is None else values['init_pop']
        plot_calc_values = {'init_pop':n0,'growth_rate':r, 'time':1}

        x_data = []
        y_data = []

        for i in range(0, math.ceil(t) + 1):
            x_data.append(i)
            if i == 0:
                pop = n0
            else:
                pop = self.calc_final_pop(plot_calc_values)
                plot_calc_values['init_pop'] = pop
            y_data.append(pop)

        plot_data = [{'x_data': x_data, 'y_data': y_data}]

        return plot_data

    @staticmethod
    def create_solver_form_from_query_params(request, post=False):
        if post:
            form = PopulationGrowthSolverForm(request.POST)
        else:
            form = PopulationGrowthSolverForm()
            for param in request.GET:
                if param in form.fields:
                   form.fields[param].initial = request.GET.get(param,None)
        return form

class BreedersEquationProblem(Problem):

    def __init__(self, solver_form):

        ranges =  {'av_starting_phen': [20.0,100.0], 'av_selected_phen': [0.1, 100.0],
                      'av_response_phen': [0.1, 100.0], 'broad_heritability': [0.0, 1.0]}

        super().__init__('Breeders Equation', solver_form, ranges=ranges)

    def solve(self):
        pass

    def generate(self):
        pass

    def calc_broad_heritability(self, values):
        st_p = values['av_starting_phen']
        se_p = values['av_selected_phen']
        re_p = values['av_response_phen']

        bh = (re_p - st_p) / (se_p - st_p)
        return bh

    def calc_response(self, values):
        st_p = values['av_starting_phen']
        se_p = values['av_selected_phen']
        bh = values['broad_heritability']

        re_p  = bh * (se_p - st_p) + st_p
        return re_p

    def calc_start(self, values):
        se_p = values['av_selected_phen']
        re_p = values['av_response_phen']
        bh = values['broad_heritability']

        st_p = (re_p  - (bh * se_p)) / (1 - bh)
        return st_p

    def calc_selected(self, values):
        st_p = values['av_starting_phen']
        re_p = values['av_response_phen']
        bh = values['broad_heritability']

        se_p = (re_p  - ((1-bh) * st_p)) / bh
        return se_p


    def calc(self, values):
        if values['broad_heritability'] is None:
            bh = self.calc_broad_heritability(values)
            return bh
        elif values['av_starting_phen'] is None:
            st_p = self.calc_start(values)
            return st_p
        elif values['av_selected_phen'] is None:
            se_p = self.calc_selected(values)
            return se_p
        elif values['av_response_phen'] is None:
            re_p = self.calc_response(values)
            return re_p
        else:
            return -1

    def calc_missing(self):
        values = {}
        for range in self.ranges:
            values[range] = self.solver_form.cleaned_data[range]
        return self.calc(values)



    def pick_field(self):
        num_fields = len(self.ranges)
        r = random.randint(0, num_fields - 1)
        picked_field = list(self.ranges.keys())[r]
        values = {picked_field: None}

        satisfactory = False
        while not satisfactory:
            for field in self.ranges:
                if field == picked_field:
                    pass
                else:
                    if isinstance(self.ranges[field][0], int):
                        r = random.randint(self.ranges[field][0], self.ranges[field][1])
                    else:
                        r = random.uniform(self.ranges[field][0], self.ranges[field][1])
                        r = round(r, 2)

                    values[field] = r
                    self.solver_form.fields[field].initial = r
                    # form.fields[field].disabled = True
                    self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
            answer = self.calc(values)
            if (answer >= self.ranges[picked_field][0]) and (answer <= self.ranges[picked_field][1]):
                satisfactory = True
        return picked_field, values


    def check_answer(self):
        #fields = ['init_pop_generator', 'final_pop_generator', 'growth_rate_generator', 'time_generator']
        form  = self.solver_form
        values = {}
        for field in self.ranges:
            values[field] = None if form.cleaned_data['answer_field'] == field else  form.cleaned_data[field]

        correct_answer_title = ''
        for field in self.ranges:
            if field == form.cleaned_data['answer_field']:
                correct_answer_title = form.fields[field].label
            else:
                form.fields[field].widget.attrs.update({'readonly': 'readonly'})

        correct_answer = self.calc(values)
        correct_answer_rounded = round(correct_answer, 2) if  isinstance(self.ranges[form.cleaned_data['answer_field']][0],float) else  round(correct_answer)#form.cleaned_data['answer_field'] == 'growth_rate' else round(correct_answer)

        supplied_answer = form.cleaned_data[form.cleaned_data['answer_field']]

        correct_flag = False
        #if form.cleaned_data['answer_field'] == 'growth_rate':
        if (isinstance(self.ranges[form.cleaned_data['answer_field']][0], float)):
            if abs(correct_answer - supplied_answer) < 0.01:
                correct_flag = True
        else:
            if abs(correct_answer - supplied_answer) < 1:
                correct_flag = True

        plot_data = self.generate_plot_data(correct_answer=correct_answer)

        return correct_answer, correct_answer_rounded, correct_answer_title, correct_flag, plot_data

    def generate_plot_data(self, correct_answer=None):


        values = {}
        for field in self.ranges:
            values[field] = None if self.solver_form.cleaned_data['answer_field'] == field else self.solver_form.cleaned_data[field]

        st_p = correct_answer if values['av_starting_phen'] is None else values['av_starting_phen']
        se_p = correct_answer if values['av_selected_phen'] is None else values['av_selected_phen']
        re_p = correct_answer if values['av_response_phen'] is None else values['av_response_phen']
        bh = correct_answer if values['broad_heritability'] is None else values['broad_heritability']


        plot_data = [{'x_data': [st_p, se_p, re_p], 'y_data': [0,0,0]}]

        return plot_data

    @staticmethod
    def create_solver_form_from_query_params(request, post=False):
        if post:
            form = BreedersEquationSolverForm(request.POST)
        else:
            form = BreedersEquationSolverForm()
            for param in request.GET:
                if param in form.fields:
                   form.fields[param].initial = request.GET.get(param,None)
        return form

class TestCrossLinkageProblem(Problem):

    ranges = {'ABC': [1, 1000], 'ABc': [1, 1000], 'AbC': [1, 1000], 'Abc': [1, 1000],
              'aBC': [1, 1000], 'aBc': [1, 1000], 'abC': [1, 1000], 'abc': [1, 1000]}

    def __init__(self, solver_form):

        super().__init__('Test Cross Linkage', solver_form, ranges=TestCrossLinkageProblem.ranges)

    def solve(self):
        pass

    def generate(self):
        pass


    def calc(self, values):

        return -1

    def calc_missing(self):
        gametes = {}
        for field in self.solver_form.cleaned_data:
            if field in self.ranges:
                gametes[field] = self.solver_form.cleaned_data[field]

        answer = Organism.calc_recombination_fractions(gametes)
        return answer

    def pick_field(self):
        num_fields = len(self.ranges)
        r = random.randint(0, num_fields - 1)
        picked_field = list(self.ranges.keys())[r]
        values = {}

        satisfactory = False
        while not satisfactory:
            for field in self.ranges:
                if isinstance(self.ranges[field][0], int):
                    r = random.randint(self.ranges[field][0], self.ranges[field][1])
                else:
                    r = random.uniform(self.ranges[field][0], self.ranges[field][1])
                    r = round(r, 2)

                values[field] = r
                self.solver_form.fields[field].initial = r
                # form.fields[field].disabled = True
                self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
            answer = self.calc(values)
            if (1 == 1):
                satisfactory = True
        return picked_field, values


    def check_answer(self):
        #fields = ['init_pop_generator', 'final_pop_generator', 'growth_rate_generator', 'time_generator']
        form  = self.solver_form
        values = {}
        for field in self.ranges:
            values[field] = None if form.cleaned_data['answer_field'] == field else  form.cleaned_data[field]
        correct_answer_title = ''
        for field in self.ranges:
            if field == form.cleaned_data['answer_field']:
                correct_answer_title = form.fields[field].label
            else:
                form.fields[field].widget.attrs.update({'readonly': 'readonly'})

        correct_answer = self.calc(values)
        correct_answer_rounded = round(correct_answer, 2) if  isinstance(self.ranges[form.cleaned_data['answer_field']][0],float) else  round(correct_answer)#form.cleaned_data['answer_field'] == 'growth_rate' else round(correct_answer)

        supplied_answer = form.cleaned_data[form.cleaned_data['answer_field']]

        correct_flag = False
        if form.cleaned_data['answer_field'] == 'growth_rate':
            if abs(correct_answer - supplied_answer) < 0.01:
                correct_flag = True
        else:
            if abs(correct_answer - supplied_answer) < 1:
                correct_flag = True

        plot_data = self.generate_plot_data(correct_answer=correct_answer)

        return correct_answer, correct_answer_rounded, correct_answer_title, correct_flag, plot_data

    def generate_plot_data(self, correct_answer=None):

        plot_data = []
        return plot_data

    def set_fields_from_gametes(self, gametes):
        for gamete in gametes:
            self.solver_form.fields[gamete].widget.attrs.update({'readonly': 'readonly'})

        pass

    @staticmethod
    def create_solver_form_from_query_params(request, post=False):
        if post:
            form = GCMSolverForm(request.POST)
        else:
            form = GCMSolverForm()
            for key in TestCrossLinkageProblem.ranges:
                form.fields[key].initial = '0'

            for param in request.GET:
                if param in form.fields:
                   form.fields[param].initial = request.GET.get(param,None)

            form.fields['answer_field'].initial = json.dumps({'phenotypes': Genome.test_cross_het_gametes_to_phenotypes()})
        return form

class HardyWeinbergProblem(Problem):

    ranges = {'obs_AA': [1, 1000], 'obs_Aa': [1, 1000], 'obs_aa': [1, 1000]}

    def __init__(self, solver_form):

        super().__init__('Hardy Weinberg', solver_form, ranges=HardyWeinbergProblem.ranges)

    def solve(self):
        pass

    def generate(self):
        pass

    def set_missing_field_in_form(self, missing_field, ans):
        self.solver_form.data = self.solver_form.data.copy()

        self.solver_form.data[missing_field] = json.dumps(ans)


    def calc_allele_frequencies(self, observed):
        A_count = observed[0]*2 + observed[1]
        tot_allele_count = sum(observed) *2
        p = A_count / tot_allele_count
        q = 1- p
        return p, q

    def calc_expected_genotype_counts(self, observed, p, q):
        exp_AA = math.pow(p, 2) * sum(observed)
        exp_Aa = 2 * p * q * sum(observed)
        exp_aa = sum(observed) - exp_AA - exp_Aa
        return [exp_AA, exp_Aa, exp_aa]

    def calc_F(self, observed, expected):
        obs_Aa_freq = observed[1] / sum(observed)
        exp_Aa_freq = expected[1] / sum(expected)
        return 1 - (obs_Aa_freq / exp_Aa_freq)

    def calc(self, values):
        observed = [values['obs_AA'],values['obs_Aa'], values['obs_aa']]
        p, q = self.calc_allele_frequencies(observed)
        expected = self.calc_expected_genotype_counts(observed, p, q)
        chisq, p_val = chisquare(observed, expected, ddof=1)
        F = self.calc_F(observed, expected)
        pop = sum(observed)

        expected = [round(exp) for exp in expected]
        F = round(F, 3)

        return {'exp_AA': expected[0], 'exp_Aa': expected[1], 'exp_aa': expected[2], 'F': F, 'p': round(p,3), 'q': round(q,3), 'pop':pop}

    def calc_missing(self):
        values = {}
        for range in self.ranges:
            values[range] = self.solver_form.cleaned_data[range]
        return self.calc(values)

    def pick_field(self):

        satisfactory = False
        while not satisfactory:
            p = random.uniform(0.01, 0.99)

            r = random.randint(0,1)
            if r == 0:
                F = 0.01
            else:
                F = random.uniform(0.01, 0.4)

            pop_sizes = [1000, 1200, 1400, 1600, 2000]
            r = random.randint(0, len(pop_sizes)-1)
            pd = PopDist(p, pop=pop_sizes[r], F = F, verbose=1)
            pd.sim_generations(1)
            print(pd.gens[-1].survived_genotypes)
            num_fields = len(self.ranges)
            r = random.randint(0, num_fields - 1)
            picked_field = 'exp_AA' #list(self.ranges.keys())[r]
            values = {}

            values['obs_AA'] = pd.gens[-1].survived_genotypes[0]
            values['obs_Aa'] = pd.gens[-1].survived_genotypes[1]
            values['obs_aa'] = pd.gens[-1].survived_genotypes[2]

            answer = self.calc(values)
            if (answer['F'] >= 0):
               satisfactory = True
               for field in self.ranges:
                    self.solver_form.fields[field].initial = values[field]
                    self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
        #         # form.fields[field].disabled = True
        #         self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})


        # satisfactory = False
        # while not satisfactory:
        #     for field in self.ranges:
        #         if isinstance(self.ranges[field][0], int):
        #             r = random.randint(self.ranges[field][0], self.ranges[field][1])
        #         else:
        #             r = random.uniform(self.ranges[field][0], self.ranges[field][1])
        #             r = round(r, 2)
        #
        #         values[field] = r
        #         self.solver_form.fields[field].initial = r
        #         # form.fields[field].disabled = True
        #         self.solver_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
        #     answer = self.calc(values)
        #     if (answer['F'] >= 0):
        #         satisfactory = True
        return picked_field, values


    def check_answer(self):
        #fields = ['init_pop_generator', 'final_pop_generator', 'growth_rate_generator', 'time_generator']
        form  = self.solver_form
        values = {}
        for field in self.ranges:
            #values[field] = None if form.cleaned_data['answer_field'] == field else  form.cleaned_data[field]
            values[field] = form.cleaned_data[field]
        correct_answer_title = 'dummy'
        for field in self.ranges:
            if field == form.cleaned_data['answer_field']:
                correct_answer_title = form.fields[field].label
            else:
                form.fields[field].widget.attrs.update({'readonly': 'readonly'})

        correct_answer = self.calc(values)
        #correct_answer_rounded = round(correct_answer, 2) if  isinstance(self.ranges[form.cleaned_data['answer_field']][0],float) else  round(correct_answer)#form.cleaned_data['answer_field'] == 'growth_rate' else round(correct_answer)

        correct_flag = {}
        #correct_flag = False

        for ans_key, ans_val in correct_answer.items():
            if ans_key == 'pop':
               #ignore
               continue
            if form.cleaned_data[ans_key] is None:
                correct_flag[ans_key] = False
            else:
                if ans_key == 'F' or ans_key == 'p' or ans_key == 'q':
                    if abs(ans_val - form.cleaned_data[ans_key]) < 0.01:
                        correct_flag[ans_key]= True
                    else:
                        correct_flag[ans_key] = False
                else:
                    if abs(ans_val - form.cleaned_data[ans_key]) < 2:
                        correct_flag[ans_key] = True
                    else:
                        correct_flag[ans_key] = False

        # if (abs(correct_answer['expected'][0] - form.cleaned_data['exp_AA'] < 0.01)) and (abs(correct_answer['expected'][1] - form.cleaned_data['exp_Aa'] < 0.01)) and  (abs(correct_answer['expected'][2] - form.cleaned_data['exp_aa'] < 0.01)) and (abs(correct_answer['F'] - form.cleaned_data['F'] < 0.01)):
        #        correct_flag = True

        plot_data = self.generate_plot_data(correct_answer=correct_answer)

        return correct_answer, correct_answer, correct_answer_title, correct_flag, plot_data

    def generate_plot_data(self, correct_answer=None):

        values = {}
        for field in self.ranges:
            values[field] = None if self.solver_form.cleaned_data['answer_field'] == field else  self.solver_form.cleaned_data[field]

        plot_data = []

        p_values = [x for x in np.arange(0, 1.01, 0.01)]

        exp_AA_values = [p*p*correct_answer['pop'] for p in  p_values]
        exp_aa_values = [(1-p)*(1-p)*correct_answer['pop'] for p in p_values]
        exp_Aa_values = [2*p*(1-p)*correct_answer['pop'] for p in p_values]
        plot_data = [{'x_data': p_values, 'y_data': exp_AA_values, 'vert_line': correct_answer['p'], 'annotations': [{'x':correct_answer['p'], 'y': values['obs_AA'], 'title':'  Observed AA count'},{'x':correct_answer['p'], 'y': values['obs_Aa'], 'title':'  Obs Aa'},{'x':correct_answer['p'], 'y': correct_answer['exp_Aa'], 'title':'  Exp Aa'}, {'x':correct_answer['p'], 'y': values['obs_aa'], 'title':'  Observed aa count'} ]},{'x_data': p_values, 'y_data': exp_Aa_values}, {'x_data': p_values, 'y_data': exp_aa_values} ]

        return plot_data

    def set_fields_from_gametes(self, gametes):
        for gamete in gametes:
            self.solver_form.fields[gamete].widget.attrs.update({'readonly': 'readonly'})

        pass

    @staticmethod
    def create_solver_form_from_query_params(request, post=False):
        if post:
            form = HardyWeinbergSolverForm(request.POST)
        else:
            form = HardyWeinbergSolverForm()
            for key in HardyWeinbergProblem.ranges:
                form.fields[key].initial = '0'

            for param in request.GET:
                if param in form.fields:
                   form.fields[param].initial = request.GET.get(param,None)

            form.fields['answer_field'].initial = None
        return form
