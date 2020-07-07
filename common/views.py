from django.shortcuts import render
from getools.popdist import PopDist
from getools.cross import Organism, GenomeTemplate, ChromosomeTemplate, Gene, Allele, AlleleSet, Genome
import plotly.graph_objs as go
import plotly
from .forms import AlleleFreakForm, CrossSimForm, PopulationGrowthSolverForm, BreedersEquationSolverForm, GCMSolverForm, HardyWeinbergSolverForm
from itertools import combinations
from scipy.stats import chisquare
import random
import math
from .models import PopGrowthProblem, BreedersEquationProblem, TestCrossLinkageProblem, HardyWeinbergProblem
import json
from django.http import JsonResponse
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


def index(request):
    logger.info('home page')
    context = {}
    return render(request, 'common/index.html', context)


def build_data(form):
    init_freq_a = form.cleaned_data['init_freq_a']
    pop_size = form.cleaned_data['pop_size']
    if pop_size == -1:
        pop_size = None
    fitnesses = [form.cleaned_data['fitness_AA'], form.cleaned_data['fitness_Aa'], form.cleaned_data['fitness_aa']]
    inbreeding_coefficient = form.cleaned_data['inbreeding_coefficient']
    num_gens = form.cleaned_data['num_gens']

    pd = PopDist(init_freq_a, genotype_fitnesses=fitnesses, pop=pop_size, F=inbreeding_coefficient, verbose=0)
    pd.sim_generations(num_gens)

    # x_data = [i for i in range(len(pd.gens))]
    # y_data = [round(gen.out_fa,3) for gen in pd.gens]
    #
    # return {'x_data': x_data,'y_data': y_data}
    return pd

def plot_graph_as_div(data_in, show_allele = 1):

    if show_allele == 1:
        line_type = 'solid'
    else:
        #line_type = 'dash'
        line_type = 'solid' #changed mind. Show both as solid

    data_list = []
    marker_colors = ['green','blue','orange','yellow','red','black','purple']
    for i,data in enumerate(data_in):
        data_list.append(go.Scatter(x=data['x_data'],y=data['y_data'],mode='lines',line={'dash': line_type, 'color': marker_colors[i % len(marker_colors)]}, name='run: ' + str(i+1),
                                    opacity=0.8))#,marker_color=marker_colors[i % len(marker_colors)]))

    if len(data_in) == 0:
        data_list.append(go.Scatter(x=[], y=[], mode='lines',
                                line={'dash': line_type, 'color': marker_colors[0 % len(marker_colors)]},
                                name='run: ' + str(0),
                                opacity=0.8))  # ,marker_color=marker_colors[i % len(marker_colors)]))

    allele_text = "a" if show_allele == 1 else "A"

    if len(data_in) == 0:
        x_limit = 400
    else:
        x_limit = data_in[0]['x_data'][-1]


    plot_div = plotly.offline.plot({"data": data_list,
                                    "layout": go.Layout(xaxis_title="Generations",
                                                        yaxis_title="Allele <b>" + allele_text + "</b> Frequency",
                                                        title="Allele '<b>" + allele_text + "'</b> - Frequencies over Generations",
                                                        yaxis=dict(
                                                            range=[0, 1]),
                                                        xaxis=dict( range=[0,x_limit]),
                                                        plot_bgcolor="rgb(240,240,240)")},
                                   output_type='div')

    return plot_div

def show_graph(request,form,add_new_plot_from_form=False, show_allele=1, auto_clear=False):

    saved_pop_dists = request.session.get('saved_pop_dists', [])

    context = {}

    if len(saved_pop_dists) == 0 and (not add_new_plot_from_form):
       context['no_data'] = True

    plot_data = []
    for saved_pop_dist in saved_pop_dists:
        pd = PopDist.pop_dist_from_json(saved_pop_dist)
        plot_data.append(pd.get_plot_data(allele = show_allele))

    if add_new_plot_from_form:
        new_pd = build_data(form)
        data = new_pd.get_plot_data(show_allele)
        plot_data.append(data)
        saved_pop_dists.append(new_pd.to_json())
        request.session['saved_pop_dists'] = saved_pop_dists
        request.session.modified = True

    #plot_div = plot_graph_as_div(plot_data, show_allele)  old code to generate plot js code n python
    plot_div = ''  #<div>Hello</div>
    context['plot_div'] = plot_div
    context['form']  = form
    context['sel_allele'] = show_allele
    context['auto_clear'] = auto_clear
    context['plot_data'] = plot_data
    context['show_allele'] = show_allele

    return render(request, "common/allele_freak.html", context=context)


def allele_freak(request):
    logger.info('Allele Freak')

    default_allele_choice = 1 # little a
    show_allele_choice = default_allele_choice
    auto_clear_choice = False


    if request.method == 'POST':

        form = AlleleFreakForm(request.POST)
        if 'show_allele' in request.POST:
            print('aha - show allele')

            if form.is_valid():
                show_allele_choice = int(form.cleaned_data['show_allele']) - 1
                auto_clear_choice = form.cleaned_data['auto_clear']
                print('allele choice selected: ',show_allele_choice)
            else:
                print('form not valid')

        if 'clear' in request.POST:
            print('clear pressed')
            request.session['saved_pop_dists'] = []
            return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        elif auto_clear_choice:
            print('clearing')
            request.session['saved_pop_dists'] = []
            return show_graph(request, form, add_new_plot_from_form=True, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        elif 'submitform' in request.POST:
           if form.is_valid():
                return show_graph(request,form,add_new_plot_from_form=True, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        else:
            return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
    else:
        form = AlleleFreakForm(initial={'show_allele':str(show_allele_choice + 1)})

    return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
    #return render(request, "common/allele_freak.html", {'form':form})


def population_growth(request):
    logger.info('Populaton Growth')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 'generator-tab'

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
                return render(request, "common/pop_growth.html", context=context)
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
                return render(request, "common/pop_growth.html", context=context)
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

    return render(request, "common/pop_growth.html", context=context)

def breeders_equation(request):
    logger.info('Breeders Equation')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 'generator-tab'

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

                return render(request, "common/breeders_equation.html", context=context)
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
                return render(request, "common/breeders_equation.html", context=context)
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

    return render(request, "common/breeders_equation.html", context=context)

def hardy_weinberg(request):
    logger.info('Hardy Weinberg')

    tab_requested = request.GET.get('tab', 'solver-tab')

    default_tab = 0 if tab_requested == 'solver-tab' else 'generator-tab'

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

                return render(request, "common/hardy_weinberg.html", context=context)
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
                return render(request, "common/hardy_weinberg.html", context=context)
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

    return render(request, "common/hardy_weinberg.html", context=context)


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


def get_phen_descriptions(genome_name):
    if genome_name == 'dog':
        phen_descriptions = ['aa - green eyes (AA or Aa = blue eyes)', 'bb - pink coat (BB or Bb = brown coat)',
                             'cc - spotted (CC or Cc = unspotted)']
    elif genome_name == 'fish':
        phen_descriptions = ['aa - grey body (AA or Aa = gold body)', 'bb - small eyes (BB or Bb = big eyes)',
                             'cc - no scales (CC or Cc = scales)']

    elif genome_name == 'pea':
        phen_descriptions = ['aa - wrinked (AA or Aa = round)', 'bb - green (BB or Bb = yellow)',
                             'cc - spotted (CC or Cc = unspotted)']
    else:
        phen_descriptions = ['phenotypes unknown','phenotypes unknown','phenotypes unknown']

    return phen_descriptions

def generate_positions(positions_in, num_traits=3):
    min_dist = 4000000

    if positions_in == 'rand':
        done = False
        while not done:
            positions = [random.randint(1000000, 80000000) for i in range(num_traits)]
            no_good= False
            for i, pos_1 in enumerate(positions):
                for j, pos_2 in enumerate(positions):
                    if i == j:
                        pass
                    else:
                        if abs(pos_1 - pos_2) < min_dist:
                            no_good= True
                            break
                if no_good:
                    break
            if no_good:
                 pass
            else:
                 done = True


    else:
        positions = [int(pos) for pos in positions_in.split(',')]

    return positions

def create_genome_template(request, positions_in = 'rand', chroms_in='rand', genome_names = ['dog','fish','pea'], use_specific_genome_name = None, num_traits=3):
    positions = generate_positions(positions_in)

    lowest_pos_index = positions.index(min(positions))
    highest_pos_index = positions.index(max(positions))

    if num_traits == 3:
        all_position_indexes = [0, 1, 2]
        for ind in range(3):
            if ind == lowest_pos_index:
                pass
            elif ind == highest_pos_index:
                pass
            else:
                middle_pos_index = ind
                break

        if chroms_in == 'rand':
            chroms = [1, 1, 1]
            if positions[middle_pos_index] - positions[lowest_pos_index] >= 42000000:
                chroms[middle_pos_index] = chroms[lowest_pos_index] + 1
            if positions[highest_pos_index] - positions[middle_pos_index] >= 42000000:
                chroms[highest_pos_index] = chroms[middle_pos_index] + 1
            else:
                chroms[highest_pos_index] = chroms[middle_pos_index]

        else:
            chroms = [int(chrom) for chrom in chroms_in.split(',')]
    else:
        if chroms_in == 'rand':
            chroms = [1 for i in range (num_traits)]
        else:
            chroms = [int(chrom) for chrom in chroms_in.split(',')]


    possible_symbols = ['A', 'B','C']

    #g1 = Gene(AlleleSet.default_alleleset_from_symbol('A'), positions[0])
    #g2 = Gene(AlleleSet.default_alleleset_from_symbol('B'), positions[1])
    #g3 = Gene(AlleleSet.default_alleleset_from_symbol('C'), positions[2])
    genes = [Gene(AlleleSet.default_alleleset_from_symbol(possible_symbols[i]), positions[i]) for i in range(num_traits)]
    #genes = [g1, g2, g3]

    chr_genes = [[] for i in range(len(chroms))]
    #chr1_genes = []
    #chr2_genes = []
    #chr3_genes = []
    for i, chrom in enumerate(chroms):
        if chrom == 1:
            chr_genes[0].append(genes[i])
        elif chrom == 2:
            chr_genes[1].append(genes[i])
        else:
            chr_genes[2].append(genes[i])
    #TODO  - in the middle of fixing this up to cater for variable number of traits (did assume 3)
    chrom_list = []

    possible_chrom_names = ['XL', 'XR', '4']

    for i, chrom in enumerate(chroms):
        if len(chr_genes[i]) > 0:
            chr = ChromosomeTemplate(possible_chrom_names[i], 350, chr_genes[i])
            chrom_list.append(chr)
    # chr1 = ChromosomeTemplate('XL', 350, chr1_genes)
    # chrom_list.append(chr1)
    # chr2 = None
    # if len(chr2_genes) > 0:
    #     chr2 = ChromosomeTemplate('XR', 400, chr2_genes)
    #     chrom_list.append(chr2)
    # chr3 = None
    # if len(chr3_genes) > 0:
    #     chr3 = ChromosomeTemplate('4', 500, chr3_genes)
    #     chrom_list.append(chr3)

    # chr2 = ChromosomeTemplate('XR',2000,[g3])

    if use_specific_genome_name is None:
        # get random genome name
        r = random.randint(0, len(genome_names) - 1)
        genome_name = genome_names[r]
        if genome_name == 'pea':  # make little less likely to generate pea
            r = random.randint(0, len(genome_names) - 1)
            genome_name = genome_names[r]
    else:
        genome_name = use_specific_genome_name

    gt = GenomeTemplate(ploidy=2, chromosomes=chrom_list, name=genome_name)

    return gt

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
                    return render(request, "common/cross_map.html", context=context)
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
                return render(request, "common/cross_map.html", context=context)


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

    if 'gcm_children' in request.session:
        del request.session['gcm_children']

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

    if default_tab == 1:
        child_list = [child._to_attr_dict() for child in children]
        request.session['gcm_children'] = child_list

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
    return render(request, "common/cross_map.html",
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

def cross_type_for_orgs(orgs):
    if orgs[0] == 0 and orgs[1] == 2:
        return '1'
    elif  orgs[0] == 1 and orgs[1] == 2:
        return '2'
    elif  orgs[0] == 1 and orgs[1] == 1:
        return '3'
    else:
        return '4'

def orgs_for_cross_type(cross_type):
    if cross_type == '1':
        return 0, 2
    elif cross_type == '2':
        return 1, 2
    elif cross_type == '3':
        return 1, 1
    else:
        return 1,1

def cross_sim(request):
    logger.info('Cross Sim Test')

    genome_name_requested = request.GET.get('genome-name', None)
    genome_names = ['dog', 'fish', 'pea']

    if genome_name_requested is None:
        # get random genome name
        r = random.randint(0, len(genome_names) - 1)
        genome_name = genome_names[r]
        if genome_name == 'pea':  # make little less likely to generate pea
            r = random.randint(0, len(genome_names) - 1)
            genome_name = genome_names[r]
    else:
        genome_name = genome_name_requested

    phen_descriptions = get_phen_descriptions(genome_name)

    max_traits = 3

    if request.method == 'POST':
        pass
    else:
        default_num_traits = int(request.GET.get('loci', '2'))
        default_cross_type = request.GET.get('cross-type', 'hybrid')
        default_gen_phen = request.GET.get('gen-phen', 'p')

        cross_type_map = {'pure': '1', 'test': '2', 'hybrid': '3'}
        if default_cross_type in cross_type_map:
            default_cross_type = cross_type_map[default_cross_type]
        else:
            default_cross_type = '3'

        sel_p1, sel_p2 = orgs_for_cross_type(default_cross_type)
        form = CrossSimForm(initial={'p1': str(sel_p1+1),'p2': str(sel_p2+1), 'alleles': str(default_num_traits), 'cross_type': default_cross_type, 'gen_phen':default_gen_phen})

        organisms = []
        for num_traits in range(1, max_traits+1):
            positions_in = ','.join([str(10000000 + (10000000 * i)) for i in range(num_traits)])
            gt = create_genome_template(request, positions_in=positions_in, num_traits=num_traits)

            organism_set = [Organism.organism_with_hom_dominant_genotype(gt),
                         Organism.organism_with_het_genotype(gt, rand_phase=True),
                         Organism.organism_with_hom_recessive_genotype(gt)]
            organisms.append(organism_set)


        request.session['cs_organisms'] = [[org._to_attr_dict() for org in organism_set] for organism_set in organisms]

        org_gen_phens = [[org.gen_phen() for org in organism_set] for organism_set in organisms]
        poss_gametes = [[org.genome.possible_gametes_formatted(dec_places=3, suppress_combine_same=True) for org in organism_set] for organism_set in organisms]
        poss_gametes_rolled_up = [[org.genome.possible_gametes_formatted(dec_places=3, suppress_combine_same=False) for org in organism_set] for organism_set in organisms]

        num_traits_ind = default_num_traits - 1
        parents = [org_gen_phens[num_traits_ind][sel_p1],org_gen_phens[num_traits_ind][sel_p2]]
        parent_poss_gametes = [poss_gametes[num_traits_ind][sel_p1],poss_gametes[num_traits_ind][sel_p2]]

        return render(request, "common/cross_sim.html",
                      context={'form':form,'gen_phen': default_gen_phen, 'num_traits': default_num_traits,'p1_ind': sel_p1, 'p2_ind': sel_p2, 'p1':organisms[num_traits_ind][sel_p1],'p2': organisms[num_traits_ind][sel_p2], 'parents':parents, 'parent_poss_gametes': parent_poss_gametes,'genome_name': genome_name, 'phen_descriptions': phen_descriptions, 'org1_phen':'a+b+c+','organims':organisms, 'orgs':org_gen_phens,'poss_gametes':poss_gametes, 'poss_gametes_rolled_up': poss_gametes_rolled_up})


def load_quiz(quiz_code):
    file_name = settings.BASE_DIR + '/static/quiz/' + quiz_code + '.json'
    with open(file_name) as json_file:
        j  = json.load(json_file)

    return j


def quiz(request):
    quiz_code_requested = request.GET.get('quiz-code', 'GENEV')

    max_questions = request.GET.get('questions', -1)

    terms = load_quiz(quiz_code_requested)
    context= {"terms": terms, 'max_questions': max_questions}

    return render(request, "common/quiz.html", context=context)

def support(request):

    return render(request, "common/support.html")

def about(request):

    return render(request, "common/about.html")