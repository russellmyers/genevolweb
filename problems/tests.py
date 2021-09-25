from django.test import TestCase, Client
from .models import PopGrowthProblem
from .forms import PopulationGrowthSolverForm
import random

# Create your tests here.


class PopGrowthModelTestCase(TestCase):

    def setUp(self):
        pass

    def test_pick(self):
        random.seed(42)
        pg = PopGrowthProblem(solver_form=PopulationGrowthSolverForm())
        res1 = pg.pick_field()
        self.assertEqual(res1, ('init_pop', {'init_pop': None, 'final_pop': 13356886, 'growth_rate': 0.15, 'time': 56}))
        res2 = pg.pick_field()
        self.assertEqual(res2, ('final_pop', {'final_pop': None, 'init_pop': 1458691, 'growth_rate': 0.12, 'time': 29}))
        res3 = pg.pick_field()
        self.assertEqual(res3, ('init_pop', {'init_pop': None, 'final_pop': 22575562, 'growth_rate': 0.04, 'time': 89}))
        res4 = pg.pick_field()
        self.assertEqual(res4, ('init_pop', {'init_pop': None, 'final_pop': 85329037, 'growth_rate': 0.04, 'time': 94}))
        res5 = pg.pick_field()
        self.assertEqual(res5, ('time', {'time': None, 'init_pop': 109131, 'final_pop': 31429110, 'growth_rate': 0.14}))
        res6 = pg.pick_field()
        self.assertEqual(res6, ('growth_rate', {'growth_rate': None, 'init_pop': 4662007, 'final_pop': 30868105,
                                                'time': 52}))
        res7 = pg.pick_field()
        self.assertEqual(res7, ('growth_rate', {'growth_rate': None, 'init_pop': 1714903,
                                                'final_pop': 22448136, 'time': 73}))
        res8 = pg.pick_field()
        self.assertEqual(res8, ('init_pop', {'init_pop': None, 'final_pop': 58181396, 'growth_rate': 0.17, 'time': 58}))


class PopGrowthViewTestCase(TestCase):
    def setUp(self):
        pass

    def test_views_health_check(self):
        c = Client()
        response = c.get('/pc/pg')
        self.assertEqual(response.status_code, 200)

    def test_views_screen(self):
        c = Client()
        response = c.get('/pc/pg')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 0)
        response = c.get('/pc/pg', {'tab': 'generator-tab'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 1)
        num_nones = 0
        for key, val in response.context['other_values'].items():
            if val is None:
                num_nones += 1
        self.assertEqual(num_nones, 1)

    def test_views_post_problem_solver(self):
        c = Client()
        response = c.post('/pc/pg', {'init_pop': '1000', 'growth_rate': '0.2', 'time': '10', 'final_pop': '',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['final_pop'], 7389)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/pg', {'init_pop': '1000', 'growth_rate': '0.3', 'time': '', 'final_pop': '10000',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['time'], 8)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/pg', {'init_pop': '', 'growth_rate': '0.3', 'time': '8', 'final_pop': '10000',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['init_pop'], 907)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/pg', {'init_pop': '907', 'growth_rate': '', 'time': '8', 'final_pop': '10000',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['growth_rate'], 0.3)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/pg', {'init_pop': '1000', 'growth_rate': '0.3', 'time': '', 'final_pop': '100',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Invalid parameters (would result in negative time). Please try different parameters')

    def test_views_post_problem_generator(self):
        c = Client()
        response = c.post('/pc/pg', {'tab': 'generator-tab', 'init_pop': '5310966', 'growth_rate': '0.03',
                                     'time': '94', 'final_pop': '89101284', 'answer_field': 'final_pop',
                                     'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], True)
        self.assertEqual(response.context['answer_rounded'], 89101284)

        response = c.post('/pc/pg', {'tab': 'generator-tab', 'init_pop': '5310966', 'growth_rate': '0.03',
                                     'time': '94', 'final_pop': '89101286', 'answer_field': 'final_pop',
                                     'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], False)
        self.assertEqual(response.context['answer_rounded'], 89101284)

        response = c.post('/pc/pg', {'tab': 'generator-tab', 'init_pop': '5310966', 'growth_rate': '0.03',
                                     'time': '94', 'final_pop': '', 'answer_field': 'final_pop',
                                     'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Please enter your answer')
