from django.shortcuts import render
import random
# from getools.cross import Organism, GenomeTemplate, ChromosomeTemplate, Gene, AlleleSet
from getools.cross import Organism
from .forms import CrossSimForm
from common.views import get_phen_descriptions, create_genome_template

import logging
logger = logging.getLogger(__name__)

# Create your views here.


def cross_type_for_orgs(orgs):
    if orgs[0] == 0 and orgs[1] == 2:
        return '1'
    elif orgs[0] == 1 and orgs[1] == 2:
        return '2'
    elif orgs[0] == 1 and orgs[1] == 1:
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
        return 1, 1


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
        form = CrossSimForm(initial={'p1': str(sel_p1+1), 'p2': str(sel_p2+1), 'alleles': str(default_num_traits),
                                     'cross_type': default_cross_type, 'gen_phen': default_gen_phen})

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
        parents = [org_gen_phens[num_traits_ind][sel_p1], org_gen_phens[num_traits_ind][sel_p2]]
        parent_poss_gametes = [poss_gametes[num_traits_ind][sel_p1], poss_gametes[num_traits_ind][sel_p2]]

        return render(request, "crosssim/cross_sim.html",
                      context={'form': form, 'gen_phen': default_gen_phen, 'num_traits': default_num_traits,
                               'p1_ind': sel_p1, 'p2_ind': sel_p2, 'p1': organisms[num_traits_ind][sel_p1],
                               'p2': organisms[num_traits_ind][sel_p2], 'parents': parents,
                               'parent_poss_gametes': parent_poss_gametes, 'genome_name': genome_name,
                               'phen_descriptions': phen_descriptions, 'org1_phen': 'a+b+c+', 'organims': organisms,
                               'orgs': org_gen_phens, 'poss_gametes': poss_gametes,
                               'poss_gametes_rolled_up': poss_gametes_rolled_up})
