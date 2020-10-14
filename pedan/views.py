from django.shortcuts import render
from .forms import PedigreeAnalyserForm
from getools.cross import ChromosomeTemplate, Gene, Pedigree, ARGenotypeInferrer, ADGenotypeInferrer, XRGenotypeInferrer, XDGenotypeInferrer, YGenotypeInferrer
import random
import math

import logging
logger = logging.getLogger(__name__)

#Create your views here.


def ped_an(request):
    '''
    Pedigree analyser

    Create random pedigree and pass to common/ped_an.html to render

    Query params:

    - inh_pattern: chrom type/inheritance type to generate (eg AR = Autosomal Recessive, XD = X-linked Dominant etc)


    :param request:
    :return:
    '''


    logger.info('Pedigree Analyser')

    inh_pattern_requested = request.GET.get('inh_pattern', None)
    if inh_pattern_requested is None:
        chrom_type_requested = None
        inh_type_requested = None
    else:
        chrom_type_requested = inh_pattern_requested[0]
        inh_type_requested = inh_pattern_requested[1]

    max_consistent_allowed = request.GET.get('max_con', None) # Max number of pedigrees allowed consistent with the pedigree being generated
    if max_consistent_allowed is not None:
        max_consistent_allowed = int(max_consistent_allowed)
    max_tries = int(request.GET.get('max_tries', 50)) # Max number of pedigrees to attempt to generate to find one which satisfies the max_consistent_allowed criteria. If exceeded, picks pedigree with min num consistent pedigrees over the limit

    debug = request.GET.get('debug', 'N')

    if request.method == 'POST':
        pass
    else:
        form = PedigreeAnalyserForm(initial={'inh_patterns': str(-1)})


        prob_mate = 0.5  # 0.9
        max_children = 4  # 8
        max_levels = 4  # 5

        if chrom_type_requested is None:
            r = random.randint(0,4)
            chrom_type = None
            if (r== 0) or (r==1):
               chrom_type = ChromosomeTemplate.AUTOSOMAL
            elif (r == 2) or (r==3):
               chrom_type = ChromosomeTemplate.X
            else: # less chance of Y
                chrom_type = ChromosomeTemplate.Y
        else:
            chrom_type = chrom_type_requested

        if chrom_type ==  ChromosomeTemplate.Y:
            inh_type = Gene.INH_PATTERN_RECESSIVE
        else:
            if inh_type_requested is None:
                r = random.randint(0,1)
                if r == 0:
                    inh_type = Gene.INH_PATTERN_RECESSIVE
                else:
                    inh_type = Gene.INH_PATTERN_DOMINANT
            else:
                inh_type = inh_type_requested

        if max_consistent_allowed is None: # not supplied in query parameter. Try to set
            if (chrom_type == ChromosomeTemplate.AUTOSOMAL):
                r = random.random()
                if r < 0.5:
                    max_consistent_allowed = 3
                else:
                    max_consistent_allowed = 2
            elif  (chrom_type == ChromosomeTemplate.X):
                if r < 0.5:
                    max_consistent_allowed = 3
                else:
                    max_consistent_allowed = 2



        min_consistent_found = math.inf
        min_consistent_pedigree = None

        done = False
        tries = 0
        while not done:
            tries += 1
            p = Pedigree(max_levels=max_levels, inh_type=inh_type, chrom_type=chrom_type,
                         prob_mate=prob_mate, max_children=max_children)
            adam = p.generate(hom_rec_partners=False)
            if len(p.all_orgs_in_pedigree()) > 5:
                actual_inferrer = None
                inferrers = [ARGenotypeInferrer(p), ADGenotypeInferrer(p), XRGenotypeInferrer(p), XDGenotypeInferrer(p),
                             YGenotypeInferrer(p)]
                num_consistent = 0
                for inferrer in inferrers:
                    if (inferrer.inh_type == inh_type) and (inferrer.chrom_type == chrom_type):
                        actual_inferrer = inferrer
                    consistent, err_msg = inferrer.infer()
                    if consistent:
                        num_consistent += 1
                        if ((chrom_type != ChromosomeTemplate.Y) and (inferrer.chrom_type  == ChromosomeTemplate.Y)):
                           #print('Found Y consistent pedigree which was not itself explicitly generated as Y linked')
                           pass


                num_afflicted = 0
                for org in p.all_orgs_in_pedigree():
                    if actual_inferrer.is_afflicted(org):
                        num_afflicted +=1
                if (num_afflicted == 0)   or (num_afflicted == len(p.all_orgs_in_pedigree())):
                    pass
                elif max_consistent_allowed is not None:
                    if num_consistent < min_consistent_found:
                        min_consistent_found = num_consistent
                        min_consistent_pedigree = p

                    if num_consistent <= max_consistent_allowed:
                       done = True
                       break
                    else:
                       if tries > max_tries:
                          p = min_consistent_pedigree
                          done = True
                          break

                else:
                    done = True
                    break

        ped_j = p.to_json()

        act_gens = []
        for org in p.all_orgs_in_pedigree():
            act_gens.append(f'{org}')
        print('Act: ')
        print(str(act_gens))

        consistent_per_inferrer = {}
        possible_genotypes_per_inferrer = {}

        inferrers = [ARGenotypeInferrer(p), ADGenotypeInferrer(p), XRGenotypeInferrer(p), XDGenotypeInferrer(p),
                     YGenotypeInferrer(p)]
        for inferrer in inferrers:
            consistent, err_msg = inferrer.infer()

            if consistent:
                if inferrer.inferrer_type in consistent_per_inferrer:
                    consistent_per_inferrer[inferrer.inferrer_type] += 1
                else:
                    consistent_per_inferrer[inferrer.inferrer_type] = 1
            else:
                consistent_per_inferrer[inferrer.inferrer_type] = 0
            #     print(f'Consistent with {inferrer.inferrer_type}')

            possible_genotypes_per_inferrer[inferrer.inferrer_type] = inferrer.all_possible_genotypes

        ped_j['consistent'] = consistent_per_inferrer
        ped_j['actual'] = chrom_type + str(inh_type)

        return render(request, "common/ped_an.html",
                      context={'form':form, 'ped_j':ped_j, 'act_gens': act_gens, 'cons_per_inferrer': consistent_per_inferrer, 'poss_gens_per_inferrer': possible_genotypes_per_inferrer, 'debug': debug})
