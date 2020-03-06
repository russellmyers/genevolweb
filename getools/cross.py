import random
debug = 0
from getools.gen import SerialiserMixin

class Allele(SerialiserMixin):
    def __init__(self,symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    @staticmethod
    def _from_attr_dict(attr_dict):
        obj = Allele(attr_dict['symbol'])
        return obj

class Gene(SerialiserMixin):
    def __init__(self,alleles,position,name = '', recessive=True):
        self.alleles = alleles
        self.position = position
        self.name = name
        self.recessive = recessive

    def __str__(self):
        return 'Name: ' + self.name + ' Pos: ' +  str(self.position) + ' Alleles: ' + '-'.join([str(allele) for allele in self.alleles])

    def distance(self,other_gene):
        return other_gene.position - self.position

    @staticmethod
    def _from_attr_dict(attr_dict):
        alleles = [Allele._from_attr_dict(al) for al in attr_dict['alleles']]
        obj = Gene(alleles,attr_dict['position'],attr_dict['name'],attr_dict['recessive'])
        return obj


class ChromosomeTemplate(SerialiserMixin):
    def __init__(self,name, size, genes_list=None):
        self.name = name
        self.size  = size
        self.genes = self.add_genes(genes_list)

    def add_genes(self,genes_list):
         return sorted(genes_list,key=lambda x:x.position)

    def positions(self):
        return [str(gene.alleles[1]) + '-' + str(gene.position) for gene in self.genes]

    def __str__(self):
        return 'ChromosomeTemplate ' + self.name + '-Size: ' + str(self.size) + ' Genes: ' + ','.join(['[Gene: ' + str(gene) + ']' for gene in self.genes])

    @staticmethod
    def _from_attr_dict(attr_dict):
        genes_list = [Gene._from_attr_dict(g) for g in attr_dict['genes']]
        obj = ChromosomeTemplate(attr_dict['name'],attr_dict['size'],genes_list)
        return obj

    def generate_random_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            r = random.randint(0, len(gene.alleles) - 1)
            actual_alleles.append(gene.alleles[r])
        return Chromosome(self, actual_alleles)

    def generate_complement_chromosome(self, other_chromosome):
        actual_alleles = []
        for i,gene in enumerate(self.genes):
            other_allele = other_chromosome.alleles[i]
            other_allele_index = gene.alleles.index(other_allele)
            allele_index = 0 if other_allele_index == 1 else 1
            actual_alleles.append(gene.alleles[allele_index])
        return Chromosome(self, actual_alleles)


    def generate_hom_recessive_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleles[-1])
        return Chromosome(self, actual_alleles)

    def generate_hom_dominant_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleles[0])
        return Chromosome(self, actual_alleles)

    def generate_het_chromosome(self):
        actual_alleles = []
        for gene in self.genes:
            actual_alleles.append(gene.alleles[-1])
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
    def __init__(self,ploidy=2,chromosomes=[],name='Unnamed_Genome'):
        self.ploidy = ploidy
        self.chromosomes = chromosomes
        self.name = name

    def __str__(self):
         return 'GenomeTemplate: ' + self.name +  ':'.join(['[' + str(ct) + ']' for ct in self.chromosomes])

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

    def generate_random_genome(self):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_random_pair(self.ploidy))
        return Genome(self,chrom_pairs)

    def generate_hom_recessive_genome(self):
        chrom_pairs = []
        for chromosome in self.chromosomes:
            chrom_pairs.append(chromosome.generate_hom_recessive_pair(self.ploidy))
        return Genome(self,chrom_pairs)

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

    def get_phase(self,alpha_sort=False):
        alleles = []
        if alpha_sort:
            alleles = [chrom.alleles_order_by_lowest_alpha() for chrom in self.chrom_pair]
        else:
            alleles = [str(chrom) for chrom in self.chrom_pair]

        if alpha_sort:
           alleles.sort()

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
                    lower_allele = allele

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

    def crossover(self):

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

    def recombine(self):

        if debug > 0:
             print('crossing over')
        return self.crossover()
        #r = random.randint(0, len(self.chrom_pair) - 1)
        #return Chromosome(self.chromosome_template,self.chrom_pair[r].alleles.copy())


    def mate(self,other_chrom_pair):

        if (self.num_genes() == 1):
            new_chrom_pair = []
            r = random.randint(0,len(self.chrom_pair)-1)
            new_chrom_pair.append(self.chrom_pair[r])
            r = random.randint(0,len(other_chrom_pair.chrom_pair)-1)
            new_chrom_pair.append(other_chrom_pair.chrom_pair[r])

            return ChromosomePair(self.chromosome_template,new_chrom_pair)
        else:
            return ChromosomePair(self.chromosome_template,[self.recombine(),other_chrom_pair.recombine()])


class Genome(SerialiserMixin):
    def __init__(self,genome_template,chromosome_pairs=[]):
        self.genome_template = genome_template
        self.chromosome_pairs = chromosome_pairs

    def __str__(self):
        out_str = ''
        for chrom_pair in self.chromosome_pairs:
            out_str += str(chrom_pair)

        str_list = []
        for i in range(int(len(out_str) / 2)):
            str_list.append(out_str[i * 2:i * 2 + 2])
        str_list.sort(key=lambda x: x[0])
        return ''.join(str_list)
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


    def mate(self,genome):
        new_chrom_pairs = []
        for i,cp in enumerate(self.chromosome_pairs):
            new_chrom_pairs.append(cp.mate(genome.chromosome_pairs[i]))
        return Genome(self.genome_template,new_chrom_pairs)


class Organism(SerialiserMixin):
    def __init__(self,genome):
       self.genome = genome

    @staticmethod
    def organism_with_random_genotype(genome_template):
        genome = genome_template.generate_random_genome()
        return Organism(genome)

    @staticmethod
    def organism_with_hom_recessive_genotype(genome_template):
        genome = genome_template.generate_hom_recessive_genome()
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

    def __str__(self):
        return str(self.genome)

    @staticmethod
    def _from_attr_dict(attr_dict):
        genome =  Genome._from_attr_dict(attr_dict['genome'])
        obj = Organism(genome)
        return obj

if __name__ == '__main__':
    debug = 0
    a1 = Allele('A')
    a2 = Allele('a')
    g1 = Gene([a1,a2],10000000)
    g2 = Gene([Allele('B'),Allele('b')],170)
    g3 = Gene([Allele('C'),Allele('c')],80000000)
    g5 = Gene([Allele('D'),Allele('d')],50000000)
    g4 = Gene([Allele('G+'),Allele('G-'),Allele('g')],150)

    print(a1)
    print(g1)

    d = g3._to_attr_dict()

    g_new = Gene._from_attr_dict(d)

    c1 = ChromosomeTemplate('3',200,[g2])



    c2 = ChromosomeTemplate('XL',350,[g1,g3,g5])

    c_attr_dict = c2._to_attr_dict()

    c2_inflated = ChromosomeTemplate._from_attr_dict(c_attr_dict)


    c3 = ChromosomeTemplate('XR',1000,[g4])
    print(c1)
    gt = GenomeTemplate(ploidy=2,chromosomes = [c1,c2,c3],name='Threechroms')
    print(gt)

    gt_attr_dict = gt._to_attr_dict()



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

    org11 = Organism.organism_with_random_genotype(gt)
    org22 = Organism.organism_with_random_genotype(gt)

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