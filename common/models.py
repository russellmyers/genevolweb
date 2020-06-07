from django.db import models

from .forms import PopulationGrowthSolverForm, PopulationGrowthGeneratorForm
import random
import math

# Create your models here.


class Problem():
    def __init__(self, title, solver_form, generator_form, ranges = {}):
        self.title = title
        self.solver_form = solver_form
        self.generator_form = generator_form
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

    @staticmethod
    def create_solver_form_from_query_params(request):
        return None

    @staticmethod
    def create_generator_form(request):
        return None


class PopGrowthProblem(Problem):

    def __init__(self, solver_form, generator_form):

        if solver_form is None:
            ranges =  {'init_pop_generator': [100, 10000000], 'final_pop_generator': [10000000, 100000000],
                      'growth_rate_generator': [0.001, 0.2], 'time_generator': [25, 100]}
        else:
            ranges =  {'init_pop': [100, 10000000], 'final_pop': [10000000, 100000000],
                      'growth_rate': [0.001, 0.2], 'time': [25, 100]}

        super().__init__('Population Growth', solver_form, generator_form, ranges=ranges)

    def solve(self):
        pass

    def generate(self):
        pass

    def calc_final_pop(self, values):
        n0 = values['init_pop_generator']
        r = values['growth_rate_generator']
        t = values['time_generator']

        nt = n0 * math.exp(r * t)
        return nt

    def calc_init_pop(self, values):
        nt = values['final_pop_generator']
        r = values['growth_rate_generator']
        t = values['time_generator']

        n0 = nt / (math.exp(r * t))
        return n0

    def calc_time(self, values):
        n0 = values['init_pop_generator']
        nt = values['final_pop_generator']
        r = values['growth_rate_generator']

        t = math.log(nt / n0) / r
        return t

    def calc_r(self, values):
        n0 = values['init_pop_generator']
        nt = values['final_pop_generator']
        t = values['time_generator']

        r = math.log(nt / n0) / t
        return r

    def calc(self, values):
        if values['final_pop_generator'] is None:
            nt = self.calc_final_pop(values)
            return nt
        elif values['init_pop_generator'] is None:
            n0 = self.calc_init_pop(values)
            return n0
        elif values['time_generator'] is None:
            t = self.calc_time(values)
            return t
        elif values['growth_rate_generator'] is None:
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

                    values[field] = r
                    self.generator_form.fields[field].initial = r
                    # form.fields[field].disabled = True
                    self.generator_form.fields[field].widget.attrs.update({'readonly': 'readonly'})
            answer = self.calc(values)
            if (answer >= self.ranges[picked_field][0]) and (answer <= self.ranges[picked_field][1]):
                satisfactory = True
        return picked_field, values

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

    @staticmethod
    def create_generator_form():
        return  PopulationGrowthGeneratorForm()