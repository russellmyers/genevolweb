import random
import math
import itertools

debug = 0
from getools.gen import SerialiserMixin

class Allele(SerialiserMixin):

    Dominant = 'D'
    Recessive = 'R'

    def __init__(self,symbol,type='R'):
        self.symbol = symbol
        self.type = type

    def __str__(self):
        return self.symbol

    def is_dom(self):
        return self.type == Allele.Dominant

    def is_rec(self):
        return self.type == Allele.Recessive

    @staticmethod
    def _from_attr_dict(attr_dict):
        obj = Allele(attr_dict['symbol'],attr_dict['type'])
        return obj

class AlleleSet(SerialiserMixin):
    def __init__(self,alleles):
        self.alleles= alleles

    @staticmethod
    def default_alleleset_from_symbol(symbol):
        alleles = []
        allele = Allele(symbol.upper(),type=Allele.Dominant)
        alleles.append(allele)
        allele = Allele(symbol.lower(),type=Allele.Recessive)
        alleles.append(allele)
        return AlleleSet(alleles)

    def dom_allele(self):
        for allele in self.alleles:
            if allele.is_dom():
                return allele
        return None

    def rec_allele(self):
        for allele in self.alleles:
            if allele.is_rec():
                return allele
        return None

    def __str__(self):
        return '-'.join([str(al) for al in self.alleles])



    @staticmethod
    def _from_attr_dict(attr_dict):
        alleles = [Allele._from_attr_dict(al) for al in attr_dict['alleles']]
        obj = AlleleSet(alleles)
        return obj

class Gene(SerialiserMixin):
    def __init__(self,alleleset,position,name = ''):
        self.alleleset = alleleset
        self.position = position
        self.name = name
        #self.recessive = recessive

    def __str__(self):
        return 'Name: ' + self.name + ' Pos: ' +  str(self.position) + ' Alleles: ' + str(self.alleleset)

    def distance(self,other_gene):
        return other_gene.position - self.position

    @staticmethod
    def _from_attr_dict(attr_dict):
        alleleset = AlleleSet._from_attr_dict(attr_dict['alleleset'])
        obj = Gene(alleleset,attr_dict['position'],attr_dict['name'])
        return obj


class ChromosomeTemplate(SerialiserMixin):
    #Class constants
    AUTOSOMAL = 'A'
    X = 'X'
    Y = 'Y'

    def __init__(self,name, size, genes_list=None, type=AUTOSOMAL):
        self.name = name
        self.size  = size
        self.type = type
        self.genes = self.add_genes(genes_list)

    def add_genes(self,genes_list):
         return sorted(genes_list,key=lambda x:x.position)

    def positions(self):
        return [str(gene.alleleset.alleles[1]) + '-' + str(gene.position) for gene in self.genes]

    def __str__(self):
        return 'ChromosomeTemplate ' + self.name +  '-Type: ' + self.type +  ' Size: ' + str(self.size) + ' Genes: ' + ','.join(['[Gene: ' + str(gene) + ']' for gene in self.genes])

    @staticmethod
    def _from_attr_dict(attr_dict):
        genes_list = [Gene._from_attr_dict(g) for g in attr_dict['genes']]
        obj = ChromosomeTemplate(attr_dict['name'],attr_dict['size'],genes_list)
        return obj

    def get_gene_from_symbol(self, symbol):
        for gene in self.genes:
            if symbol in str(gene.alleleset):
                return gene
        return None


    def generate_random_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            r = random.randint(0, len(gene.alleleset.alleles) - 1)
            actual_alleles.append(gene.alleleset.alleles[r])
        return Chromosome(self, actual_alleles)

    def generate_complement_chromosome(self, other_chromosome):
        actual_alleles = []
        for i,gene in enumerate(self.genes):
            other_allele = other_chromosome.alleles[i]
            other_allele_index = gene.alleleset.alleles.index(other_allele)
            allele_index = 0 if other_allele_index == 1 else 1
            actual_alleles.append(gene.alleleset.alleles[allele_index])
        return Chromosome(self, actual_alleles)


    def generate_hom_recessive_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleleset.rec_allele())  #(gene.alleles[-1])
        return Chromosome(self, actual_alleles)

    def generate_hom_dominant_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleleset.dom_allele())  #(gene.alleles[0])
        return Chromosome(self, actual_alleles)

    def generate_het_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleleset.alleles[-1])
        return Chromosome(self, actual_alleles)

    def generate_random_pair(self,ploidy):
        chrom_pair = []
        for i in range(ploidy):
            chromosome = self.generate_random_chromosome()
            chrom_pair.append(chromosome)
        return ChromosomePair(self,chrom_pair)


    def generate_hom_recessive_pair(self, ploidy):
        chrom_pair = []
        for i in range(ploidy):
            chromosome = self.generate_hom_recessive_chromosome()
            chrom_pair.append(chromosome)
        return ChromosomePair(self, chrom_pair)

    def generate_hom_dominant_pair(self, ploidy):
        chrom_pair = []
        for i in range(ploidy):
            chromosome = self.generate_hom_dominant_chromosome()
            chrom_pair.append(chromosome)
        return ChromosomePair(self, chrom_pair)

    def generate_het_pair(self, ploidy, rand_phase=False):
        chrom_pair = []
        if rand_phase:
            chromosome_1 = self.generate_random_chromosome()
            chromosome_2 = self.generate_complement_chromosome(chromosome_1)
        else:
            chromosome_1 = self.generate_hom_dominant_chromosome()
            chromosome_2 = self.generate_hom_recessive_chromosome()
        chrom_pair = [chromosome_1,chromosome_2]
        return ChromosomePair(self, chrom_pair)


class GenomeTemplate(SerialiserMixin):
    def __init__(self,ploidy=2,chromosomes=[],X_chromosome=None, Y_chromosome=None, name='Unnamed_Genome'):
        self.ploidy = ploidy
        self.chromosomes = chromosomes # autosomal chromosomes
        self.X_chromosome = X_chromosome
        self.Y_chromosome = Y_chromosome
        self.name = name

    def __str__(self):

        if self.X_chromosome is None:
            X_chrom = 'None'
        else:
            X_chrom = str(self.X_chromosome)


        if self.Y_chromosome is None:
            Y_chrom = 'None'
        else:
            Y_chrom = str(self.Y_chromosome)

        return 'GenomeTemplate: ' + self.name +  ':'.join(['[' + str(ct) + ']' for ct in self.chromosomes]) + ' X chrom: ' + X_chrom + ' Y chrom: '+ Y_chrom

    @staticmethod
    def _from_attr_dict(attr_dict):
        chromosome_templates  = [ChromosomeTemplate._from_attr_dict(ct) for ct in attr_dict['chromosomes']]
        obj = GenomeTemplate(ploidy=attr_dict['ploidy'],chromosomes=chromosome_templates, name=attr_dict['name'])
        return obj

    def positions(self):
        posns = []
        for chromosome_template in self.chromosomes:
            posns.extend(chromosome_template.positions())

        return posns

    def chromosome_names(self):
        return [chrom.name for chrom in self.chromosomes]

    def generate_random_sex_pair(self, sex=None):
        if self.X_chromosome is None:
            return None


        chrom_1 = self.X_chromosome.generate_random_chromosome() # at least 1 X
        if (self.Y_chromosome is None) or (sex == Genome.FEMALE):
            r = 0
        elif sex == Genome.MALE:
            r = 1
        else:
            r = random.randint(0,1)
        chrom_2_template = self.X_chromosome if r == 0 else self.Y_chromosome
        chrom_2 = chrom_2_template.generate_random_chromosome()
        return ChromosomeSexPair([chrom_1,chrom_2],self.X_chromosome, chrom_2_template)

    def generate_random_genome(self, sex=None):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_random_pair(self.ploidy))
        sex_pair = self.generate_random_sex_pair(sex=sex)
        return Genome(self,chrom_pairs, sex_pair = sex_pair)

    def generate_hom_recessive_genome(self):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_hom_recessive_pair(self.ploidy))
        return Genome(self,chrom_pairs)

    def generate_hom_dominant_genome(self):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_hom_dominant_pair(self.ploidy))
        return Genome(self, chrom_pairs)

    def generate_het_genome(self, rand_phase=False):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_het_pair(self.ploidy,rand_phase=rand_phase))
        return Genome(self,chrom_pairs)

class Chromosome(SerialiserMixin):
    def __init__(self,chromosome_template,alleles):
        self.chromosome_template = chromosome_template
        self.alleles = alleles

    # @staticmethod
    # def generate_random_chromosome(genes):
    #     actual_alleles = []
    #     for gene in genes:
    #         r = random.randint(0, len(gene) - 1)
    #         actual_alleles.append(gene.alleles[r])
    #     return Chromosome(actual_alleles)

    def __copy__(self):
        new_alleles = self.alleles.copy()
        return Chromosome(self.chromosome_template,new_alleles)

    def __str__(self):

       chrom_gen_str = ''.join([str(allele) for allele in self.alleles])
       return chrom_gen_str

    def alleles_order_by_lowest_alpha(self):
        if str(self.alleles[0]).upper() > str(self.alleles[-1]).upper():
            return ''.join([str(allele) for allele in self.alleles[::-1]])
        else:
            return ''.join([str(allele) for allele in self.alleles])



    @staticmethod
    def _from_attr_dict(attr_dict):
        alleles = [Allele._from_attr_dict(al) for al in attr_dict['alleles']]
        chrom_template = ChromosomeTemplate._from_attr_dict(attr_dict['chromosome_template'])
        obj = Chromosome(chrom_template,alleles)
        return obj



class ChromosomePair(SerialiserMixin):
    def __init__(self,chromosome_template,chrom_pair):
        self.chromosome_template = chromosome_template
        self.chrom_pair = chrom_pair

    def __str__(self):
        out_str = ''
        for i in range(self.num_genes()):
            allele_pair = self.get_allele_pair(i)
            out_str +=  ''.join(allele_pair)

        return out_str

    @staticmethod
    def _from_attr_dict(attr_dict):
        chrom_pair =  [Chromosome._from_attr_dict(chrom) for chrom in attr_dict['chrom_pair']]
        chrom_template = ChromosomeTemplate._from_attr_dict(attr_dict['chromosome_template'])
        obj = ChromosomePair(chrom_template, chrom_pair)
        return obj

    def get_phase(self,alpha_sort=False, show_dist = True):
        alleles = []
        if alpha_sort:
            alleles = [chrom.alleles_order_by_lowest_alpha() for chrom in self.chrom_pair]
        else:
            alleles = [str(chrom) for chrom in self.chrom_pair]

        if alpha_sort:
           alleles.sort()

        if show_dist:
           prev_gen = None
           dists = []
           for i, allele_symbol in enumerate(alleles[0]):
               gene = self.chromosome_template.get_gene_from_symbol(allele_symbol)
               if i == 0:
                   prev_gene = gene
               else:
                   dists.append(gene.distance(prev_gene))
                   prev_gene = gene
           dists = [math.floor(abs(dist / 10000000)) * '-' for dist in dists]
           alleles_with_dist = ['','']
           for i in range(len(alleles[0])):
               if i == 0:
                  alleles_with_dist[0] = alleles[0][i]
                  alleles_with_dist[1] = alleles[1][i]
               else:
                  alleles_with_dist[0] += dists[i-1] + alleles[0][i]
                  alleles_with_dist[1] += dists[i - 1] + alleles[1][i]

           alleles = alleles_with_dist
           #alleles[0] = alleles[0][0] + dists[0] + alleles[0][1] + dists[1] + alleles[0][2]
           #alleles[1] = alleles[1][0] + dists[0] + alleles[1][1] + dists[1] + alleles[1][2]



        out_str = '//'.join(alleles)
        return out_str

    def get_parental_gamete(self,parent_num):
        gamete = ''
        for allele in self.chrom_pair[parent_num].alleles:
            gamete += allele.symbol
        return gamete




    def num_genes(self):
        return len(self.chromosome_template.genes)


    def get_allele_pair(self,i, sort=True):
        allele_pair= []
        for chrom in self.chrom_pair:
            allele_pair.append(str(chrom.alleles[i]))
        if sort:
            allele_pair.sort()
        return allele_pair

    def phenotype(self,alpha_sort=True):
        phen = ''
        allele_pairs = []
        for i in range(self.num_genes()):
            allele_pair = self.get_allele_pair(i)
            allele_pairs.append(allele_pair)

        if alpha_sort:
            allele_pairs.sort(key=lambda x:x[1])
        for allele_pair in allele_pairs:
            num_lower = 0
            lower_allele = ''

            for allele in allele_pair:
                if not (allele.isupper()):
                    num_lower +=1
                lower_allele = allele.lower()


            phen += lower_allele
            phen += '+' if num_lower < 2 else '-'
        return phen






    def pick_random_alleles(self):

        new_alleles = []
        for i in range(self.num_genes()):
            r = random.randint(0, len(self.chrom_pair)-1)
            new_alleles.append(self.chrom_pair[r].alleles[i])

        return Chromosome(self.chromosome_template,new_alleles)


    def all_unlinked(self):
        all_positions = [gene.position for gene in self.chromosome_template.genes]
        highest = max(all_positions)
        lowest = min(all_positions)
        if ((highest - lowest) >= 50000000):
            return True
        return False

    def allele_pairs(self):
        pairs = []
        for  i in range(self.num_genes()):
            pair = [(self.chrom_pair[0].alleles[i],0),(self.chrom_pair[1].alleles[i],1)]
            pairs.append(pair)

        return pairs

    def possible_gametes(self):
        probs = self.crossover_probabilities()


        possibles = list(itertools.product(*self.allele_pairs()))

        possibles_with_prob = []

        for possible in possibles:
            prob = 0.5
            for i, (allele,phase) in enumerate(possible):
                if i == 0:
                    prev_phase = phase
                else:
                    this_prob = 1 - probs[i-1] if phase == prev_phase else  probs[i-1]
                    prob *= this_prob
                    prev_phase = phase


                #print(allele,phase)

            alleles_only = [p[0] for p in possible]
            found = False
            for p_with_prob in possibles_with_prob:
                if alleles_only == p_with_prob[0]:
                    p_with_prob[1] += prob
                    p_with_prob[2] += 1
                    found = True
                    break
            if not found:
                possibles_with_prob.append([alleles_only, prob, 1, len(possibles)])

        return possibles_with_prob

    def crossover_probabilities(self):

        probs = []

        for i in range(self.num_genes()-1):
            gene1 = self.chromosome_template.genes[i]
            gene2 = self.chromosome_template.genes[i+1]
            dist = gene1.distance(gene2)
            if debug > 0:
                print('dist: ', gene1, gene2, dist)
            prob_crossover = (dist / 1000000) / 100.0
            if debug > 0:
                print('prob: ',prob_crossover)
            if prob_crossover > 0.5:
                prob_crossover = 0.5
            probs.append(prob_crossover)

        return probs

    def meiosis(self):

        probs = self.crossover_probabilities()

        crossovers = []
        for i in range(self.num_genes()-1):
            gene1 = self.chromosome_template.genes[i]
            gene2 = self.chromosome_template.genes[i+1]
            dist = gene1.distance(gene2)
            if debug > 0:
                print('dist: ', gene1, gene2, dist)
            prob_crossover = (dist / 1000000) / 100.0
            if debug > 0:
                print('prob: ',prob_crossover)
            if prob_crossover >= 0.5:
                crossovers.append('Rand')
            else:
                r = random.random()
                if r < prob_crossover:
                    crossovers.append('Yes')
                else:
                    crossovers.append('No')

        if debug > 0:
            print(crossovers)


        if len(crossovers) == 0:  # Only 1 gene. Pick chromosome at random
            r = random.randint(0, len(self.chrom_pair) - 1)
            return self.chrom_pair[r]

        new_alleles = []
        for i,cr in enumerate(crossovers):
            if i == 0: # Pick which chrom pair to start with
                pair_num = random.randint(0, len(self.chrom_pair) - 1)
                if debug > 0:
                    print('first choice: ', pair_num, self.chrom_pair[pair_num].alleles[i])
                new_alleles.append(self.chrom_pair[pair_num].alleles[i])
            if crossovers[i] == 'Rand':
                pair_num = random.randint(0, len(self.chrom_pair) - 1)
                if debug > 0:
                    print('random choice', pair_num, self.chrom_pair[pair_num].alleles[i+1])
                new_alleles.append(self.chrom_pair[pair_num].alleles[i+1])
            else:
                if crossovers[i] == 'Yes':
                    pair_num = 0 if pair_num == 1 else 1
                if debug > 0:
                    print(crossovers[i] + ' choice',pair_num,self.chrom_pair[pair_num].alleles[i+1] )
                new_alleles.append(self.chrom_pair[pair_num].alleles[i+1])

        if debug > 0:
            print('new alleles: ')
            for allele in new_alleles:
                print(allele)

        return Chromosome(self.chromosome_template, new_alleles)



    def mate(self,other_chrom_pair):

        # if (self.num_genes() == 1):
        #     new_chrom_pair = []
        #     r = random.randint(0,len(self.chrom_pair)-1)
        #     new_chrom_pair.append(self.chrom_pair[r])
        #     r = random.randint(0,len(other_chrom_pair.chrom_pair)-1)
        #     new_chrom_pair.append(other_chrom_pair.chrom_pair[r])
        #
        #     return ChromosomePair(self.chromosome_template,new_chrom_pair)
        # else:
        #     return ChromosomePair(self.chromosome_template,[self.meiosis(),other_chrom_pair.meiosis()])

        return ChromosomePair(self.chromosome_template, [self.meiosis(), other_chrom_pair.meiosis()])

class ChromosomeSexPair(ChromosomePair, SerialiserMixin):
    def __init__(self,chrom_pair, chrom_1_template, chrom_2_template):
        super(ChromosomeSexPair,self).__init__(chrom_1_template, chrom_pair)

        self.chrom_1_template = chrom_1_template # ie first of chrom pair
        self.chrom_2_template = chrom_2_template # ie second of chrom pair

    def get_allele_X_pair(self,i, sort=True):
        pass

    def get_allele_Y(self,i, sort=True):
        pass

    def get_allele_pair(self, i, sort=True):
        # TODO fill in allele pair logic:
        allele_pair = []
        if self.chrom_1_template == self.chrom_2_template: #Assume female
           for chrom in self.chrom_pair:
               allele_pair.append('X' + str(chrom.alleles[i]))

        else:
           allele_pair.append('X' + str(self.chrom_pair[0].alleles[i]))
           allele_pair.append('Y_')

        if sort:
            allele_pair.sort()
        return allele_pair

    def get_allele_X_pair(self, i, sort=True):
            # TODO fill in allele pair logic:
            allele_pair = []
            if self.chrom_1_template == self.chrom_2_template:  # Assume female
                for chrom in self.chrom_pair:
                    allele_pair.append('X' + str(chrom.alleles[i]))

            else:
                allele_pair.append('X' + str(self.chrom_pair[0].alleles[i]))
                allele_pair.append('Y ')

            if sort:
                allele_pair.sort()
            return allele_pair

    def get_allele_Y_pair(self, i, sort=True):
            # TODO fill in allele pair logic:
            allele_pair = []
            if self.chrom_1_template == self.chrom_2_template:
                return ''


            allele_pair.append('Y' + str(self.chrom_pair[1].alleles[i]) + 'X ')


            if sort:
                allele_pair.sort()
            return allele_pair

        #self.get_allele_X_pair(i, sort=sort)
        # default to just X-linked

        # allele_pair = []
        # for chrom in self.chrom_pair:
        #     allele_pair.append(str(chrom.alleles[i]))
        # if sort:
        #     allele_pair.sort()
        # return allele_pair

    def num_genes(self):
         return len(self.chromosome_template.genes)
        #TODO cater for Y chromosome - add these genes

    def num_X_genes(self):
        return len(self.chrom_1_template.genes)

    def num_Y_genes(self):
        if self.chrom_1_template == self.chrom_2_template:
            return 0

        return len(self.chrom_2_template.genes)

    def meiosis(self):

        if self.chrom_2_template == ChromosomeTemplate.X:
            return super().meiosis()
        else:
            r = random.randint(0,1) # male or female!
            return self.chrom_pair[r]

        # crossovers = []
        # for i in range(self.num_genes() - 1):
        #     gene1 = self.chromosome_template.genes[i]
        #     gene2 = self.chromosome_template.genes[i + 1]
        #     dist = gene1.distance(gene2)
        #     if debug > 0:
        #         print('dist: ', gene1, gene2, dist)
        #     prob_crossover = (dist / 1000000) / 100.0
        #     if debug > 0:
        #         print('prob: ', prob_crossover)
        #     if prob_crossover >= 0.5:
        #         crossovers.append('Rand')
        #     else:
        #         r = random.random()
        #         if r < prob_crossover:
        #             crossovers.append('Yes')
        #         else:
        #             crossovers.append('No')
        #
        # if debug > 0:
        #     print(crossovers)
        #
        # if len(crossovers) == 0:  # Only 1 gene. Pick chromosome at random
        #     r = random.randint(0, len(self.chrom_pair) - 1)
        #     return self.chrom_pair[r]
        #
        # new_alleles = []
        # for i, cr in enumerate(crossovers):
        #     if i == 0:  # Pick which chrom pair to start with
        #         pair_num = random.randint(0, len(self.chrom_pair) - 1)
        #         if debug > 0:
        #             print('first choice: ', pair_num, self.chrom_pair[pair_num].alleles[i])
        #         new_alleles.append(self.chrom_pair[pair_num].alleles[i])
        #     if crossovers[i] == 'Rand':
        #         pair_num = random.randint(0, len(self.chrom_pair) - 1)
        #         if debug > 0:
        #             print('random choice', pair_num, self.chrom_pair[pair_num].alleles[i + 1])
        #         new_alleles.append(self.chrom_pair[pair_num].alleles[i + 1])
        #     else:
        #         if crossovers[i] == 'Yes':
        #             pair_num = 0 if pair_num == 1 else 1
        #         if debug > 0:
        #             print(crossovers[i] + ' choice', pair_num, self.chrom_pair[pair_num].alleles[i + 1])
        #         new_alleles.append(self.chrom_pair[pair_num].alleles[i + 1])
        #
        # if debug > 0:
        #     print('new alleles: ')
        #     for allele in new_alleles:
        #         print(allele)
        #
        # return Chromosome(self.chromosome_template, new_alleles)

    def mate(self, other_chrom_pair):

        # if (self.num_genes() == 1):
        #     new_chrom_pair = []
        #     r = random.randint(0,len(self.chrom_pair)-1)
        #     new_chrom_pair.append(self.chrom_pair[r])
        #     r = random.randint(0,len(other_chrom_pair.chrom_pair)-1)
        #     new_chrom_pair.append(other_chrom_pair.chrom_pair[r])
        #
        #     return ChromosomePair(self.chromosome_template,new_chrom_pair)
        # else:
        #     return ChromosomePair(self.chromosome_template,[self.meiosis(),other_chrom_pair.meiosis()])

        chrom_1 = self.meiosis()
        chrom_2 = other_chrom_pair.meiosis()

        return ChromosomeSexPair([chrom_1,chrom_2], chrom_1.chromosome_template, chrom_2.chromosome_template)




    def __str__(self):
        out_str = ''

        for i in range(self.num_X_genes()):
            allele_pair = self.get_allele_X_pair(i)
            out_str +=  ''.join(allele_pair)

        out_str += ' '

        for i in range(self.num_Y_genes()):
            allele_pair = self.get_allele_Y_pair(i)
            out_str += ''.join(allele_pair)

        return out_str


class Genome(SerialiserMixin):

    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'

    def __init__(self,genome_template,chromosome_pairs=[],sex_pair=None):
        self.genome_template = genome_template
        self.chromosome_pairs = chromosome_pairs
        self.sex_pair =  sex_pair

    def __str__(self):

        out_str = ''

        #out_str += self.sex() + ': '
        for chrom_pair in self.chromosome_pairs:
            out_str += str(chrom_pair)



        str_list = []
        for i in range(int(len(out_str) / 2)):
            str_list.append(out_str[i * 2:i * 2 + 2])
        str_list.sort(key=lambda x: x[0].upper())

        out_str = ''.join(str_list)

        if self.sex_pair is None:
            pass
        else:
            out_str += '  ' + str(self.sex_pair)

        if self.sex() == Genome.UNKNOWN:
            return out_str
        else:
            return self.sex() + ': ' + out_str
        #return out_str

    @staticmethod
    def _from_attr_dict(attr_dict):
        chrom_pairs = [ChromosomePair._from_attr_dict(chrom_pair) for chrom_pair in attr_dict['chromosome_pairs']]
        genome_template =GenomeTemplate._from_attr_dict(attr_dict['genome_template'])
        obj = Genome(genome_template,chromosome_pairs=chrom_pairs)
        return obj

    def get_phase(self,alpha_sort=False):
        chrom_phases = [chrom_pair.get_phase(alpha_sort) for chrom_pair in self.chromosome_pairs]
        if alpha_sort:
           chrom_phases.sort(key=lambda x: x.upper())
        phase = ';'.join(chrom_phases)
        return phase

    def get_parental_gamete(self,parent_num,sort_alpha=False):
        gamete_per_pair =  [chromosome_pair.get_parental_gamete(parent_num) for chromosome_pair in self.chromosome_pairs]
        gamete = ''.join(gamete_per_pair)
        if sort_alpha:
           gamete_chr_list = list(gamete)
           gamete_chr_list.sort(key=lambda x: x.upper())
           gamete = ''.join(gamete_chr_list)
        return gamete

    def genotype(self):
        p1 = []
        p2 = []
        for  chrom_pair in self.chromosome_pairs:
            p1.append(str(chrom_pair.chrom_pair[0]))
            p2.append(str(chrom_pair.chrom_pair[1]))
        if self.sex_pair is None:
            pass
        else:
            p1.append(str(self.sex_pair.chrom_pair[0]))
            p2.append(str(self.sex_pair.chrom_pair[1]))

        return '\n'.join(['//'.join(p1),'//'.join(p2)])

    def phenotype(self,sort_alpha=True):
        phen = ''
        for chromosome_pair in self.chromosome_pairs:
            phen += chromosome_pair.phenotype()

        if sort_alpha:
            phen_list = []
            for i in range(int(len(phen) / 2)):
                phen_list.append(phen[i*2:i*2+2])
            phen_list.sort(key=lambda x: x[0])
            return ''.join(phen_list)


        return phen

    def gen_phen(self):
        return {'gen':str(self),'phen':self.phenotype(), 'gen_phase':self.genotype()}


    def possible_gametes(self):
        all_possibles_with_prob = []
        for i, cp in enumerate(self.chromosome_pairs):
            possibles_with_prob  = cp.possible_gametes()
            all_possibles_with_prob.append(possibles_with_prob)

        possibles = list(itertools.product(*all_possibles_with_prob))

        combined_possibles = []
        for possible in possibles:
            combined_alleles = []
            combined_freq = 1
            combined_prob = 1
            combined_tot_possible = 1
            for chrom_possible in possible:
                combined_alleles.extend(chrom_possible[0])
                combined_freq *= chrom_possible[1]
                combined_prob *= chrom_possible[2]
                combined_tot_possible *= chrom_possible[3]
            combined_possibles.append([combined_alleles, combined_freq, combined_prob, combined_tot_possible])


        return combined_possibles

    def possible_gametes_formatted(self, dec_places=3):
        possibles = [[''.join([str(p) for p in possible[0]]),round(possible[1],dec_places),possible[2],possible[3]] for possible in self.possible_gametes()]
        return possibles

    def mate(self, other_genome):
        new_chrom_pairs = []
        for i,cp in enumerate(self.chromosome_pairs):
            new_chrom_pairs.append(cp.mate(other_genome.chromosome_pairs[i]))

        if self.sex_pair is None:
            new_sex_pair = None
        else:
            new_sex_pair = self.sex_pair.mate(other_genome.sex_pair)
        return Genome(self.genome_template,new_chrom_pairs, new_sex_pair)

    def sex(self):
        if self.sex_pair is None:
            return Genome.UNKNOWN

        for chrom in self.sex_pair.chrom_pair:
            if chrom.chromosome_template.type == ChromosomeTemplate.Y:
                return Genome.MALE
        return Genome.FEMALE

class Organism(SerialiserMixin):
    def __init__(self,genome):
       self.genome = genome

    @staticmethod
    def organism_with_random_genotype(genome_template, sex=None):
        genome = genome_template.generate_random_genome(sex=sex)
        return Organism(genome)

    @staticmethod
    def organism_with_hom_recessive_genotype(genome_template):
        genome = genome_template.generate_hom_recessive_genome()
        return Organism(genome)

    @staticmethod
    def organism_with_hom_dominant_genotype(genome_template):
        genome = genome_template.generate_hom_dominant_genome()
        return Organism(genome)

    @staticmethod
    def organism_with_het_genotype(genome_template,rand_phase=False):
        genome = genome_template.generate_het_genome(rand_phase=rand_phase)
        return Organism(genome)

    def mate(self,other_org):
        new_genome = self.genome.mate(other_org.genome)
        return Organism(new_genome)


    def genotype(self):
        return self.genome.genotype()

    def gen_phen(self):
        return self.genome.gen_phen()

    def __str__(self):
        return str(self.genome)

    @staticmethod
    def _from_attr_dict(attr_dict):
        genome =  Genome._from_attr_dict(attr_dict['genome'])
        obj = Organism(genome)
        return obj


    @staticmethod
    def unique_genotypes(organisms):
        unique_gens = {}
        for organism in organisms:
            if str(organism) in unique_gens:
                unique_gens[str(organism)] +=1
            else:
                unique_gens[str(organism)] = 1
        return unique_gens

    @staticmethod
    def unique_phenotypes(organisms):
        unique_phens = {}
        for organism in organisms:
            phen = organism.genome.phenotype()
            if phen in unique_phens:
                unique_phens[phen] +=1
            else:
                unique_phens[phen] = 1
        return unique_phens

if __name__ == '__main__':
    debug = 0
    #a1 = Allele('A')
    #a2 = Allele('a')
    alleles_a = AlleleSet.default_alleleset_from_symbol('A')
    g1 = Gene(alleles_a,10000000)
    g2 = Gene(AlleleSet.default_alleleset_from_symbol('B'),170)
    g3 = Gene(AlleleSet.default_alleleset_from_symbol('C'),80000000)
    g5 = Gene(AlleleSet.default_alleleset_from_symbol('D'),50000000)
    g4 = Gene(AlleleSet.default_alleleset_from_symbol('G'),150)
    g6 = Gene(AlleleSet.default_alleleset_from_symbol('E'),30000000)
    g7 = Gene(AlleleSet.default_alleleset_from_symbol('F'),90000000)

    print(str(alleles_a))
    print(g1)

    d = g1._to_attr_dict()
    g_new = Gene._from_attr_dict(d)

    d = g3._to_attr_dict()

    g_new = Gene._from_attr_dict(d)

    c1 = ChromosomeTemplate('3',200,[g2])

    c2 = ChromosomeTemplate('XL',350,[g1,g3,g5])

    c_attr_dict = c2._to_attr_dict()

    c2_inflated = ChromosomeTemplate._from_attr_dict(c_attr_dict)


    c3 = ChromosomeTemplate('XR',1000,[g4])
    print(c1)

    c4 = ChromosomeTemplate('XChrom',30000000,[g6],type=ChromosomeTemplate.X)
    c5 = ChromosomeTemplate('YChrom', 10000000, [g7], type=ChromosomeTemplate.Y)


    gt = GenomeTemplate(ploidy=2,chromosomes = [c1,c2,c3], X_chromosome=c4, Y_chromosome=c5, name='Fivechroms')
    print(str(gt))

    gt_attr_dict = gt._to_attr_dict()


    gt_prob_test = GenomeTemplate(ploidy=2,chromosomes = [c2], name='Probtest')
    org_prob_test = Organism.organism_with_het_genotype(gt_prob_test, rand_phase=True)
    print(org_prob_test.genome.possible_gametes_formatted())
    print('org prob test genotype: ',org_prob_test.genotype())


    org = Organism.organism_with_random_genotype(gt)
    print(org)

    org_attr_dict = org._to_attr_dict()


    ch1 = ChromosomeTemplate('3',100,[g1])
    ch2 = ChromosomeTemplate('XL-group1',300,[g2])
    gt2 = GenomeTemplate(ploidy=2,chromosomes = [ch1,ch2],name='Twochroms')
    gt2_attr_dict = gt2._to_attr_dict()
    gt2_inflated = GenomeTemplate._from_attr_dict(gt2_attr_dict)
    print(gt2_inflated)

    org1 = Organism.organism_with_random_genotype(gt2)
    print('org1: ',org1)

    org1_deflated = org1._to_attr_dict()
    org1_inflated = Organism._from_attr_dict(org1_deflated)
    print('org1 inflated: ',org1_inflated)

    print('gam1: ',org1.genome.get_parental_gamete(0))
    print('gam2: ', org1.genome.get_parental_gamete(1))

    org2 = Organism.organism_with_random_genotype(gt2)
    print('org2: ',org2)
    child = org1.mate(org2)
    print('child: ',child)


    print('org1: \n',org1.genotype())
    print('org2: \n',org2.genotype())

    new = org1.mate(org2)
    print('new:\n', new.genotype())

    org11 = Organism.organism_with_random_genotype(gt, sex=Genome.MALE)
    org22 = Organism.organism_with_random_genotype(gt, sex=Genome.FEMALE)

    org11.genome.chromosome_pairs[1].possible_gametes()
    print(str(org22))
    print('Org11')
    print(org11.genotype())
    print('Org22')
    print(org22.genotype())
    new33 = org11.mate(org22)
    print('New33')
    print(new33.genotype())
    print(new33)

    children = []
    for i in range(50):
        children.append(org11.mate(org22))

    print('A\u00B2') #Superscript
    print('A\u2082') #subscript
    print('X\u00BFX\u208f')
    print('org11: ',org11)
    print('org22: ',org22)
    if debug > 0:
        print('Children:')
        for child in children:
         print(child)

    gt_linkage = GenomeTemplate(ploidy=2, chromosomes=[c2])
    print(gt)

    org_hom = Organism.organism_with_hom_recessive_genotype(gt_linkage)
    print(org_hom)
    print (org_hom.genotype())

    org_het = Organism.organism_with_het_genotype(gt_linkage, rand_phase=True)
    print(org_het)
    print (org_het.genotype())

    print('het gam1: ', org_het.genome.get_parental_gamete(0))
    print('het gam2: ', org_het.genome.get_parental_gamete(1))

    children = []
    for i in range(1000):
        children.append(org_het.mate(org_hom))

    print('child1 gam1: ', children[0].genome.get_parental_gamete(0,sort_alpha=True))
    print('child1 gam2: ', children[0].genome.get_parental_gamete(1,sort_alpha=True))
    print('child2 gam1: ', children[1].genome.get_parental_gamete(0,sort_alpha=True))
    print('child2 gam2: ', children[1].genome.get_parental_gamete(1,sort_alpha=True))
    genotypes = {}
    for child in children:
        genotype = child.genotype()
        if genotype in genotypes:
           genotypes[genotype] +=1
        else:
            genotypes[genotype] = 1
        #print(child)

    print('org het: ',org_het.genotype())
    print('org hom: ',org_hom.genotype())
    print(genotypes)

    print (org_hom.genome.chromosome_pairs[0].phenotype())