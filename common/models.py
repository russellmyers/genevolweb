from django.db import models
import json

from .forms import PopulationGrowthSolverForm, BreedersEquationSolverForm, GCMSolverForm
import random
import math
from getools.cross import Organism, Genome

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
