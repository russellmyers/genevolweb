from django.shortcuts import render
import random
# from getools.cross import Gene, ChromosomeTemplate, GenomeTemplate, AlleleSet
from getools.cross import Gene, ChromosomeTemplate, GenomeTemplate, AlleleSet
from django.http import HttpResponse


import logging
logger = logging.getLogger(__name__)


def index(request):
    logger.info('home page')
    context = {}
    return render(request, 'common/index.html', context)


def support(request):

    return render(request, "common/support.html")


def about(request):

    return render(request, "common/about.html")


def show_request_meta(request):
    # For diagnostic purposes only
    var = request.GET.get('var', None)
    val = ''
    if var is None:
        for key, item in request.META.items():
            val += f'{str(key)}: {str(item)}<br>'
        return HttpResponse(val)
    val = request.META.get(var, 'Not found')
    return HttpResponse(f'{var}: {val}')


    x = 1

def set_session_var(request):
    session_var = request.GET.get('var', None)
    if session_var is not None:
        try:
            session_var_name, session_var_value = session_var.split(':')
            request.session[session_var_name] = session_var_value
        except Exception as e:
            logger.error(f'Invalid session var query parameter setting. Error: {e}')
            return HttpResponse("<p>Did not set session var</p>")
    return HttpResponse("<p>Set session var ok</p>")


def get_phen_descriptions(genome_name):
    if genome_name == 'dog':
        phen_descriptions = ['aa - pink coat (AA or Aa = brown coat)', 'bb - tailless (BB or Bb = tail)',
                             'cc - spotted (CC or Cc = unspotted)']
    elif genome_name == 'fish':
        phen_descriptions = ['aa - grey body (AA or Aa = gold body)', 'bb - small eyes (BB or Bb = big eyes)',
                             'cc - no scales (CC or Cc = scales)']

    elif genome_name == 'pea':
        phen_descriptions = ['aa - wrinked (AA or Aa = round)', 'bb - green (BB or Bb = yellow)',
                             'cc - spotted (CC or Cc = unspotted)']
    else:
        phen_descriptions = ['phenotypes unknown', 'phenotypes unknown', 'phenotypes unknown']

    return phen_descriptions


def generate_positions(positions_in, num_traits=3):
    min_dist = 4000000
    positions = []

    if positions_in == 'rand':
        done = False
        while not done:
            positions = [random.randint(1000000, 80000000) for _ in range(num_traits)]
            no_good = False
            for i, pos_1 in enumerate(positions):
                for j, pos_2 in enumerate(positions):
                    if i == j:
                        pass
                    else:
                        if abs(pos_1 - pos_2) < min_dist:
                            no_good = True
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


def create_genome_template(request, positions_in='rand', chroms_in='rand', genome_names=['dog', 'fish', 'pea'],
                           use_specific_genome_name=None, num_traits=3):
    positions = generate_positions(positions_in)

    lowest_pos_index = positions.index(min(positions))
    highest_pos_index = positions.index(max(positions))

    if num_traits == 3:
        middle_pos_index = None
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
            chroms = [1 for _ in range(num_traits)]
        else:
            chroms = [int(chrom) for chrom in chroms_in.split(',')]

    possible_symbols = ['A', 'B', 'C']

    # g1 = Gene(AlleleSet.default_alleleset_from_symbol('A'), positions[0])
    # g2 = Gene(AlleleSet.default_alleleset_from_symbol('B'), positions[1])
    # g3 = Gene(AlleleSet.default_alleleset_from_symbol('C'), positions[2])
    genes = [Gene(AlleleSet.default_alleleset_from_symbol(possible_symbols[i]), positions[i])
             for i in range(num_traits)]
    # genes = [g1, g2, g3]

    chr_genes = [[] for _ in range(len(chroms))]
    # chr1_genes = []
    # chr2_genes = []
    # chr3_genes = []
    for i, chrom in enumerate(chroms):
        if chrom == 1:
            chr_genes[0].append(genes[i])
        elif chrom == 2:
            chr_genes[1].append(genes[i])
        else:
            chr_genes[2].append(genes[i])
    # TODO  - in the middle of fixing this up to cater for variable number of traits (did assume 3)
    chrom_list = []

    possible_chrom_names = ['XL', 'XR', '4']

    for i, chrom in enumerate(chroms):
        if len(chr_genes[i]) > 0:
            chr_t = ChromosomeTemplate(possible_chrom_names[i], 350, chr_genes[i])
            chrom_list.append(chr_t)
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

    gt = GenomeTemplate(ploidy=2, chromosome_templates=chrom_list, name=genome_name)

    return gt
