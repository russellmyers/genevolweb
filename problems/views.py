from django.shortcuts import render
from .forms import PopulationGrowthSolverForm, BreedersEquationSolverForm, GCMSolverForm, HardyWeinbergSolverForm
from itertools import combinations
from scipy.stats import chisquare
from .models import PopGrowthProblem, BreedersEquationProblem, TestCrossLinkageProblem, HardyWeinbergProblem
import json
from django.http import JsonResponse
#from getools.cross import Organism, Genome
from genutils.cross import Organism, Genome
from common.views import get_phen_descriptions, create_genome_template


import logging
logger = logging.getLogger(__name__)

# Create your views here.

def population_growth(request):
    logger.info('Populaton Growth')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 1

    context = {}

    if request.method == 'POST':

        if 'solverSubmit' in request.POST:
            default_tab = 0
            pg = PopGrowthProblem(PopGrowthProblem.create_solver_form_from_query_params(request, post=True))
            form = pg.solver_form
            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                ans = pg.calc_missing()
                context['answer'] = ans
                context['answer_title'], missing_field = pg.missing_field()
                pg.set_missing_field_in_form(missing_field, ans)
                context['plot_data'] = pg.generate_plot_data(correct_answer=ans)
                return render(request, "problems/pop_growth.html", context=context)
            else:
                print('solver form not valid')
        else:
            default_tab = 1
            pg = PopGrowthProblem(PopulationGrowthSolverForm(request.POST))
            form = pg.solver_form
            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                context['answer'], context['answer_rounded'], context['answer_title'], context['correct_flag'], context['plot_data'] = pg.check_answer()
                context['chosen_target'] = form.cleaned_data['answer_field']
                return render(request, "problems/pop_growth.html", context=context)
            else:
                print('generator form not valid')

        context['form'] = form
        context['default_tab'] = default_tab

    else:
        if default_tab == 0:
            pg = PopGrowthProblem(PopGrowthProblem.create_solver_form_from_query_params(request))
            form = pg.solver_form
        else:
            pg = PopGrowthProblem(PopulationGrowthSolverForm())
            form = pg.solver_form
            chosen_target, other_values = pg.pick_field()
            form.fields['answer_field'].initial = chosen_target
            context['chosen_target'] = chosen_target
            context['other_values'] = other_values

        context['form'] = form
        context['default_tab'] = default_tab

    return render(request, "problems/pop_growth.html", context=context)

def breeders_equation(request):
    logger.info('Breeders Equation')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 1

    context = {}

    if request.method == 'POST':

        if 'solverSubmit' in request.POST:
            default_tab = 0
            be =  BreedersEquationProblem(BreedersEquationProblem.create_solver_form_from_query_params(request, post=True))
            form = be.solver_form

            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                ans = be.calc_missing()
                context['answer'] = ans
                context['answer_title'], missing_field = be.missing_field()
                be.set_missing_field_in_form(missing_field, ans)
                context['plot_data'] =be.generate_plot_data(correct_answer=ans)

                return render(request, "problems/breeders_equation.html", context=context)
            else:
                print('solver form not valid')
        else:
            default_tab = 1
            be = BreedersEquationProblem(BreedersEquationSolverForm(request.POST))
            form = be.solver_form
            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                #context['answer_title'], context['answer'], context['plot_data'] = pg_calc_missing(form)
                context['answer'], context['answer_rounded'], context['answer_title'], context['correct_flag'], context['plot_data'] = be.check_answer()
                context['chosen_target'] = form.cleaned_data['answer_field']
                return render(request, "problems/breeders_equation.html", context=context)
            else:
                print('generator form not valid')

        context['form'] = form
        context['default_tab'] = default_tab

    else:
        if default_tab == 0:
            be = BreedersEquationProblem(BreedersEquationProblem.create_solver_form_from_query_params(request))
            form = be.solver_form

        else:
            be =  BreedersEquationProblem(BreedersEquationSolverForm())
            form = be.solver_form
            chosen_target, other_values = be.pick_field()
            form.fields['answer_field'].initial = chosen_target
            context['chosen_target'] = chosen_target
            context['other_values'] = other_values

        context['form'] = form
        context['default_tab'] = default_tab

    return render(request, "problems/breeders_equation.html", context=context)

def hardy_weinberg(request):
    logger.info('Hardy Weinberg')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 1

    context = {}

    if request.method == 'POST':

        if 'solverSubmit' in request.POST:
            default_tab = 0
            hw =  HardyWeinbergProblem(HardyWeinbergProblem.create_solver_form_from_query_params(request, post=True))
            form = hw.solver_form

            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                ans = hw.calc_missing()
                context['answer'] = ans
                missing_field = 'answer'
                hw.set_missing_field_in_form(missing_field, ans)
                context['answer_title'] = 'answer_field'
                context['plot_data'] =hw.generate_plot_data(correct_answer=ans)

                return render(request, "problems/hardy_weinberg.html", context=context)
            else:
                print('solver form not valid')
        else:
            default_tab = 1
            hw = HardyWeinbergProblem(HardyWeinbergSolverForm(request.POST))
            form = hw.solver_form
            if form.is_valid():
                context['default_tab'] = default_tab
                context['form'] = form
                #context['answer_title'], context['answer'], context['plot_data'] = pg_calc_missing(form)
                context['answer'], context['answer_rounded'], context['answer_title'], context['correct_flag'], context['plot_data'] = hw.check_answer()
                context['chosen_target'] = form.cleaned_data['answer_field']
                return render(request, "problems/hardy_weinberg.html", context=context)
            else:
                print('generator form not valid')

        context['form'] = form
        context['default_tab'] = default_tab

    else:
        if default_tab == 0:
            hw = HardyWeinbergProblem(HardyWeinbergProblem.create_solver_form_from_query_params(request))
            form = hw.solver_form

        else:
            hw =  HardyWeinbergProblem(HardyWeinbergSolverForm())
            form = hw.solver_form
            chosen_target, other_values = hw.pick_field()
            form.fields['answer_field'].initial = chosen_target
            context['chosen_target'] = None #chosen_target
            context['other_values'] = other_values

        context['form'] = form
        context['default_tab'] = default_tab

    return render(request, "problems/hardy_weinberg.html", context=context)


def children_stats(children):

    num_samples = len(children)
    phenotypes = {}
    for child in children:
        phenotype = child.genome.phenotype()
        if phenotype in phenotypes:
            phenotypes[phenotype] += 1
        else:
            phenotypes[phenotype] = 1
        # print(child)

    # Get all combinations of [2, 1, 3]
    # and length 2
    combos = combinations([i for i in range(3)], 2)
    # TODO remove hard coded 3 above

    phen_combinations = {}

    comb_list = list(combos)

    phen_combinations_per_pair = [{} for i in range(len(comb_list))]
    for phenotype, count in phenotypes.items():
        #print(phenotype, count)
        for i, comb in enumerate(comb_list):
            #print(comb)
            phen_comb = phenotype[comb[0] * 2:comb[0] * 2 + 2] + phenotype[comb[1] * 2:comb[1] * 2 + 2]
            #print(phen_comb)
            if phen_comb in phen_combinations:
                phen_combinations[phen_comb] += count
            else:
                phen_combinations[phen_comb] = count

            if phen_comb in phen_combinations_per_pair[i]:
                phen_combinations_per_pair[i][phen_comb] += count
            else:
                phen_combinations_per_pair[i][phen_comb] = count

    for phen_combs in phen_combinations_per_pair:
        observed = [count for key, count in phen_combs.items()]
        chisq, p = chisquare(observed, ddof=1)
        phen_combs['abbrev'] =  list(phen_combs.keys())[0].replace('+','')
        phen_combs['abbrev'] = phen_combs['abbrev'].replace('-','')
        phen_combs['p'] = '{:.2e}'.format(p)

    #print(phen_combinations)
    phen_combinations_list = [(key, count) for key, count in phen_combinations.items()]
    phen_combinations_list.sort(key=lambda x: x[1])

    phenotypes_list = [(key, count) for key, count in phenotypes.items()]
    phenotypes_list.sort(key=lambda x: x[1], reverse=True)
    parentals = [phenotypes_list[0], phenotypes_list[1]]
    double_crossovers = [phenotypes_list[-2], phenotypes_list[-1]]
    double_crossovers_count = 0
    for dc in double_crossovers:
        double_crossovers_count += dc[1]

    pairs_cis = {}
    for phen_combination, count in phen_combinations.items():
        if phen_combination[1] == phen_combination[3]:
            alleles = phen_combination[0] + phen_combination[2]
            if alleles in pairs_cis:
                pairs_cis[alleles] += count
            else:
                pairs_cis[alleles] = count

    #print(pairs_cis)

    pairs_list = [(key, count) for key, count in pairs_cis.items()]
    pairs_list = [[pair[0], pair[1]] if pair[1] < num_samples / 2 else [pair[0], num_samples - pair[1]] for pair in
                  pairs_list]
    pairs_list.sort(key=lambda x: x[1])
    pairs_list[-1][1] += 2 * double_crossovers_count

    dists = [(key, round(count / num_samples * 100, 2)) for key, count in pairs_list]

    recomb_fraction_list = [(key, count) for key, count in pairs_cis.items()]
    recomb_fraction_list = [[pair[0], pair[1] / num_samples] if pair[1] < num_samples / 2 else [pair[0], (
            num_samples - pair[1]) / num_samples] for pair in
                            recomb_fraction_list]
    recomb_fraction_list.sort(key=lambda x: x[0])
    tmp = recomb_fraction_list[2]
    recomb_fraction_list[2] = recomb_fraction_list[1].copy()
    recomb_fraction_list[1] = tmp.copy()

    recomb_fraction_list_with_p = []
    for rf in recomb_fraction_list:
        rf_with_p = rf[:]
        rf_with_p.append(-1)
        for phen_combs in phen_combinations_per_pair:
            if phen_combs['abbrev']== rf_with_p[0]:
               rf_with_p[-1] = phen_combs['p']
               break

        recomb_fraction_list_with_p.append(rf_with_p)


    gamete_counts_het = {}
    for child in children:

        gamete = child.genome.get_parental_gamete(0, sort_alpha=True)
        if gamete in gamete_counts_het:
            gamete_counts_het[gamete] += 1
        else:
            gamete_counts_het[gamete] = 1

    logger.debug('gcm Gamete counts het' + str(gamete_counts_het))
    return phenotypes, pairs_cis, dists, parentals, double_crossovers, recomb_fraction_list, pairs_list, phen_combinations_per_pair, gamete_counts_het, recomb_fraction_list_with_p

def create_children(org_het, org_hom_rec, num_samples=1000):
    children = []
    for i in range(num_samples):
        children.append(org_het.mate(org_hom_rec))

    return children





def parse_het_phase(request, phase):
    chroms = phase.split(';')
    first = ''
    for chrom in chroms:
        first = first + chrom.split('//')[0]
    first = first.replace('-','')
    linkage = 'LL'
    if len(chroms) == 3:
        linkage = 'UU'
    elif len(chroms) == 2:
        if len(chroms[0].split('//')[0].replace('-','')) == 1:
            linkage =  'UL'
        else:
            linkage = 'LU'
    else:
        linkage = 'LL'

    return {'order': first, 'linkage': linkage }


def gcm_update_type(request):
    cross_type = request.GET.get('cross-type','g')
    request.session['gcm_cross_type'] = cross_type
    logger.debug('gcm cross type updated via ajax:' + cross_type)
    return JsonResponse(status=200, data={'Updated ok':cross_type})


def cross_map(request):

    logger.info('Cross Map')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 1

    genome_name_requested = request.GET.get('genome-name', None)

    context = {}

    genome_names = ['dog','fish','pea']


    positions_in = request.GET.get('pos','rand')
    chroms_in = request.GET.get('chroms','rand')

    proposed = {'order': 'ABC',
                'linkage' : 'LL',
                'rd1' : 0.0,
                'rd2' : 0.0,
                'rd3' : 0.0
                }


    num_samples = 1000

    if request.method == 'POST':
        try:
             org_het = Organism._from_attr_dict(request.session['gcm_org_het'])
             org_hom_rec = Organism._from_attr_dict(request.session['gcm_org_hom_rec'])
        except Exception as e:
                print('No organisms in session',e)

        if   'solverSubmit' in request.POST:
                default_tab = 0
                tcl = TestCrossLinkageProblem(TestCrossLinkageProblem.create_solver_form_from_query_params(request, post=True))
                form = tcl.solver_form
                if form.is_valid():
                    context['default_tab'] = default_tab
                    context['form'] = form
                    ans = tcl.calc_missing()
                    context['answer'] = ans
                    proposed = {}
                    proposed['order'] = ans['parental_ordered']
                    proposed['rd1'] = ans['recombination_fractions'][0][1]
                    proposed['rd2'] = ans['recombination_fractions'][1][1]
                    proposed['rd3'] = ans['recombination_fractions'][2][1]
                    proposed['linkage'] = ans['linkages']
                    proposed['phenotypes'] = ans['phenotypes']
                    context['proposed'] = proposed
                    tcl.solver_form.data = tcl.solver_form.data.copy()
                    tcl.solver_form.data['answer_field'] = json.dumps(proposed)

                    context['recomb_fraction_list_with_p'] = ans['recombination_fractions']
                    context['org_het_phase'] = ans['parental_ordered_formatted']

                    context['show_answer_div_below'] = True

                    genome_name = org_het.genome.genome_template.name
                    phen_descriptions = get_phen_descriptions(genome_name)
                    context['org1'] =org_het
                    context['org1_phen'] = org_het.genome.phenotype()
                    context['org2'] = org_hom_rec
                    context['org2_phen'] = org_hom_rec.genome.phenotype()
                    context['genome_name'] = genome_name
                    context['phen_descriptions'] = phen_descriptions

                    cross_type = request.session.get('gcm_cross_type', 'g')
                    context['cross_type'] = cross_type

                    #context['answer_title'], missing_field = tcl.missing_field()
                    #tcl.set_missing_field_in_form(missing_field, ans)
                    #context['plot_data'] = tcl.generate_plot_data(correct_answer=ans)
                    return render(request, "problems/cross_map.html", context=context)
                else:
                    print('solver form not valid')
                    context['default_tab'] = default_tab
                    context['form'] = form
                    #ans = tcl.calc_missing()
                    context['answer'] = None
                    proposed = {'order': 'ABC',
                                'linkage': 'LL',
                                'rd1': 0.0,
                                'rd2': 0.0,
                                'rd3': 0.0
                                }
                    proposed['phenotypes'] = Genome.test_cross_het_gametes_to_phenotypes()
                    context['proposed'] = proposed

                    context['recomb_fraction_list_with_p'] = None
                    context['org_het_phase'] = None

                    context['show_answer_div_below'] = False

                    genome_name = org_het.genome.genome_template.name
                    phen_descriptions = get_phen_descriptions(genome_name)
                    context['org1'] =org_het
                    context['org1_phen'] = org_het.genome.phenotype()
                    context['org2'] = org_hom_rec
                    context['org2_phen'] = org_hom_rec.genome.phenotype()
                    context['genome_name'] = genome_name
                    context['phen_descriptions'] = phen_descriptions

                    cross_type = request.session.get('gcm_cross_type', 'g')
                    context['cross_type'] = cross_type
                return render(request, "problems/cross_map.html", context=context)


        else:
                logger.error('Unexpected POST in cross_map. Only expect solverSubmit')

    else:
        pass

    # GET (or invalid post)
    cross_type = request.GET.get('cross-type')
    if cross_type is None:
       cross_type = request.session.get('gcm_cross_type', 'g')
    else:
       request.session['gcm_cross_type'] = cross_type

    show_cross = True
    show_answer_div_below = True

    num_samples = 1000

    gt = create_genome_template(request, chroms_in=chroms_in, positions_in=positions_in, use_specific_genome_name=genome_name_requested)

    org_het = Organism.organism_with_het_genotype(gt, rand_phase=True)
   # print(org_het)
   # print(org_het.genotype())
    request.session['gcm_org_het'] = org_het._to_attr_dict()

    org_hom_rec = Organism.organism_with_hom_recessive_genotype(gt)
    #print(org_hom_rec)
    #print (org_hom_rec.genotype())
    request.session['gcm_org_hom_rec'] = org_hom_rec._to_attr_dict()

    if default_tab == 1:
        logger.debug('gcm Creating children')
        children = create_children(org_het, org_hom_rec, num_samples=num_samples)
        logger.debug('gcm Getting children stats')
        phenotypes, pairs_cis, dists, parentals, double_crossovers, recomb_fraction_list, pairs_list, phen_combinations_per_pair, parental_gametes_het, recomb_fraction_list_with_p = children_stats(
            children)
    else:
        phenotypes = None
        pairs_cis = None
        dists = None
        parentals = None
        double_crossovers = None
        recomb_fraction_list = None
        pairs_list = None
        phen_combinations_per_pair = None
        parental_gametes_het = None
        recomb_fraction_list_with_p = None

    show_cross = True
    org_het_phase = org_het.genome.get_phase(alpha_sort=True)
    parsed_order = parse_het_phase(request, org_het_phase)

    positions = org_het.genome.genome_template.positions()

    genome_name = org_het.genome.genome_template.name
    phen_descriptions = get_phen_descriptions(genome_name)

    phen_descriptions = get_phen_descriptions(gt.name)

    if  default_tab ==0:
        tcl = TestCrossLinkageProblem(TestCrossLinkageProblem.create_solver_form_from_query_params(request, post=False))
        show_answer_div_below = False
    else:
        tcl = TestCrossLinkageProblem(GCMSolverForm(initial=parental_gametes_het))
        tcl.set_fields_from_gametes(parental_gametes_het)
        show_answer_div_below = True

    form = tcl.solver_form

    proposed['phenotypes'] = Genome.test_cross_het_gametes_to_phenotypes()

    tst = org_het.genome.phenotype()
    tst = org_hom_rec.genome.phenotype()


    return render(request, "problems/cross_map.html",
                  context={'genome_name': genome_name, 'phen_descriptions': phen_descriptions,
                           'org_het_phase': org_het_phase,
                           'show_cross': show_cross, 'cross_type': cross_type, 'positions_in': positions_in,
                           'positions': positions, 'chroms_in': chroms_in, 'org1': org_het,
                           'org1_phen': org_het.genome.phenotype(), 'org2': org_hom_rec,
                           'org2_phen': org_hom_rec.genome.phenotype(), 'children_phenotypes': phenotypes,
                           'pairs_cis': pairs_cis, 'dists': dists, 'parentals': parentals,
                           'double_crossovers': double_crossovers, 'recomb_fraction_list': recomb_fraction_list,
                           'pairs_list': pairs_list, 'phen_combs_per_pair': phen_combinations_per_pair,
                           'parental_gametes_het': parental_gametes_het,
                           'recomb_fraction_list_with_p': recomb_fraction_list_with_p,
                           'proposed': proposed,
                           'form': form,
                           'show_answer_div_below': show_answer_div_below,
                           'parsed_order': parsed_order,
                           'default_tab': default_tab
                           })


    #return render(request, "common/cross_map_old.html", context={'phen_descriptions': phen_descriptions,  'org_het_phase':org_het_phase,'show_cross': show_cross, 'cross_type': cross_type, 'positions_in':positions_in,'positions':positions, 'chroms_in':chroms_in,'org1':org_het,'org1_phen':org_het.genome.phenotype(),'org2':org_hom_rec,'org2_phen':org_hom_rec.genome.phenotype(),'children_phenotypes':phenotypes,'pairs_cis':pairs_cis,'dists':dists, 'parentals':parentals,'double_crossovers':double_crossovers,'recomb_fraction_list':recomb_fraction_list, 'pairs_list':pairs_list,'phen_combs_per_pair':phen_combinations_per_pair})
