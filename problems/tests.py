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

class BreedersEquationViewTestCase(TestCase):
    def setUp(self):
        pass

    def test_views_health_check(self):
        c = Client()
        response = c.get('/pc/be')
        self.assertEqual(response.status_code, 200)

    def test_views_screen(self):
        c = Client()
        response = c.get('/pc/be')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 0)
        response = c.get('/pc/be', {'tab': 'generator-tab'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 1)
        num_nones = 0
        for key, val in response.context['other_values'].items():
            if val is None:
                num_nones += 1
        self.assertEqual(num_nones, 1)

    def test_views_post_problem_solver(self):
        c = Client()
        response = c.post('/pc/be', {'av_starting_phen': '1000', 'av_selected_phen': '1200', 'av_response_phen': '1100', 'broad_heritability': '',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['broad_heritability'], 0.5)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/be', {'av_starting_phen': '1000', 'av_selected_phen': '1200', 'av_response_phen': '', 'broad_heritability': '0.5',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['av_response_phen'], 1100)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/be', {'av_starting_phen': '1000', 'av_selected_phen': '', 'av_response_phen': '1100', 'broad_heritability': '0.5',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['av_selected_phen'], 1200)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/be', {'av_starting_phen': '', 'av_selected_phen': '1200', 'av_response_phen': '1100', 'broad_heritability': '0.5',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['av_starting_phen'], 1000)
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)



        response = c.post('/pc/be', {'av_starting_phen': '1000', 'av_selected_phen': '1200', 'av_response_phen': '1100',
                                     'broad_heritability': '0.5',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})

        form = response.context['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Please leave 1 field missing')


        response = c.post('/pc/be', {'av_starting_phen': '1000', 'av_selected_phen': '1200', 'av_response_phen': '1300',
                                     'broad_heritability': '',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})

        form = response.context['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Average Response Phenotype must be between Average Starting Phenotype and Average Selected Phenotype')

    def test_views_post_problem_generator(self):
        c = Client()
        response = c.post('/pc/be', {'tab': 'generator-tab', 'av_starting_phen': '1000', 'av_selected_phen': '1200',
                                     'av_response_phen': '1100', 'broad_heritability': '0.5',
                                     'answer_field': 'broad_heritability', 'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], True)
        self.assertEqual(response.context['answer_rounded'], 0.5)

        response = c.post('/pc/be', {'tab': 'generator-tab', 'av_starting_phen': '1000', 'av_selected_phen': '1200',
                                     'av_response_phen': '1100', 'broad_heritability': '0.4',
                                     'answer_field': 'broad_heritability', 'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], False)
        self.assertEqual(response.context['answer_rounded'], 0.5)

        response = c.post('/pc/be', {'tab': 'generator-tab', 'av_starting_phen': '1000', 'av_selected_phen': '1200',
                                     'av_response_phen': '1100', 'broad_heritability': '',
                                     'answer_field': 'broad_heritability', 'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Please enter your answer')


class HardyWeinBergViewTestCase(TestCase):
    def setUp(self):
        pass

    def test_views_health_check(self):
        c = Client()
        response = c.get('/pc/hw')
        self.assertEqual(response.status_code, 200)

    def test_views_screen(self):
        c = Client()
        response = c.get('/pc/hw')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 0)
        response = c.get('/pc/hw', {'tab': 'generator-tab'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 1)
        num_nones = 0
        for key, val in response.context['other_values'].items():
            if val is None:
                num_nones += 1
        self.assertEqual(num_nones, 0)

    def test_views_post_problem_solver(self):
        c = Client()
        response = c.post('/pc/hw', {'obs_AA': '25', 'obs_Aa': '50', 'obs_aa': '25',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        ans = response.context['answer']
        form = response.context['form']
        self.assertEqual(ans, {'exp_AA': 25, 'exp_Aa': 50, 'exp_aa': 25, 'F': 0.0, 'p': 0.5, 'q': 0.5, 'pop': 100})
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)

        response = c.post('/pc/hw', {'obs_AA': '0', 'obs_Aa': '0', 'obs_aa': '0',
                                     'answer_field': '', 'solverSubmit': 'Calculate'})
        form = response.context['form']
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'][0], 'Please enter data')

    def test_views_post_problem_generator(self):
        c = Client()
        response = c.post('/pc/hw', {'tab': 'generator-tab', 'obs_AA': '25', 'obs_Aa': '50', 'obs_aa': '25',
                                     'p': '0.5', 'q': '0.5', 'exp_AA': '25', 'exp_Aa': '50', 'exp_aa': '25', 'F': '0.0',
                                     'answer_field': 'answer', 'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], {'exp_AA': True, 'exp_Aa': True, 'exp_aa': True, 'F': True,
                                                            'p': True, 'q': True})

        response = c.post('/pc/hw', {'tab': 'generator-tab', 'obs_AA': '50', 'obs_Aa': '50', 'obs_aa': '50',
                                     'p': '0.5', 'q': '0.5', 'exp_AA': '25', 'exp_Aa': '50', 'exp_aa': '25', 'F': '0.0',
                                     'answer_field': 'answer', 'generatorSubmit': 'Check Answer'})
        form = response.context['form']
        self.assertEqual(response.context['correct_flag'], {'exp_AA': False, 'exp_Aa': False, 'exp_aa': False,
                                                            'F': False, 'p': True, 'q': True})


class TestCrossLinkageViewTestCase(TestCase):
    def setUp(self):
        pass

    def test_views_health_check(self):
        c = Client()
        response = c.get('/pc/cross_map')
        self.assertEqual(response.status_code, 200)

    def test_views_screen(self):
        c = Client()
        response = c.get('/pc/cross_map')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 0)
        response = c.get('/pc/cross_map', {'tab': 'generator-tab'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_tab'], 1)
        num_nones = 0


    def test_views_post_problem_solver(self):
        c = Client()
        response = c.post('/pc/cross_map', {'ABC': '100', 'ABc': '100', 'AbC': '100', 'Abc': '100',
                                            'aBC': '100', 'aBc': '100', 'abC': '100', 'abc': '100',
                                            'answer_field': '{"phenotypes": {"ABC": "A+B+C+", "ABc": "A+B+c-", "AbC": "A+b-C+", "Abc": "A+b-c-", "aBC": "a-B+C+", "aBc": "a-B+c-", "abC": "a-b-C+", "abc": "a-b-c-"}}', 'solverSubmit': 'Calculate'})
        ans = response.context['answer']
        form = response.context['form']
        self.assertEqual(ans, '{"order": "ABC", "rd1": 0.5, "rd2": 0.5, "rd3": 0.5, '
                              '"linkage": "UU", "phenotypes": {"ABC": "A+B+C+", "ABc": "A+B+c-",'
                              ' "AbC": "A+b-C+", "Abc": "A+b-c-", "aBC": "a-B+C+", "aBc": "a-B+c-",'
                              ' "abC": "a-b-C+", "abc": "a-b-c-"}}')
        self.assertEqual(form.data['solverSubmit'], 'Calculate')
        self.assertEqual(len(form.errors), 0)


    def test_views_post_problem_generator(self):
        c = Client()
