// Model classes

class PunnettSquare {
    //static InheritanceAutosomal = 1;
    //static InheritanceXLinked = 2;

    constructor(inheritanceType, femaleParent, maleParent, numTraits, genPhen, genomeName) {
        this.inheritanceType = inheritanceType;
        this.femaleParent = femaleParent;
        this.maleParent = maleParent;
        this.numTraits = numTraits;
        this.genPhen = genPhen;
        this.genomeName = genomeName;
    }

    getNumTraits() {
        return this.numTraits;
    }

    getGametes(parent) {
        var gametes = [];
        for (var i = 0; i < parent.length; ++i) {
            gametes.push(parent[i][0]);
        }
        return gametes;

    }


    maleGametes() {
        return this.getGametes(this.maleParent);

    }

    femaleGametes() {
        return this.getGametes(this.femaleParent);
        //return this.femaleParent.getGametes();
    }

    combine(gametes1, gametes2) {
        var combined = [];

        for (var i = 0; i < gametes1.length; ++i) {
            if (gametes2.charAt(i) == gametes2.charAt(i).toUpperCase()) {
                combined.push(gametes2.charAt(i));
                combined.push(gametes1.charAt(i));
            } else {
                combined.push(gametes1.charAt(i));
                combined.push(gametes2.charAt(i));
            }

        }

        return combined.join('');


    }

    uniquePhenotypes() {
        var unique= [];

        var uniqueDict = {}
        var possPhenotypes = this.possiblePhenotypes();
        for (var r = 0; r < possPhenotypes.length;++r) {
            for (var c = 0; c < possPhenotypes[r].length; ++c) {
                var phen = possPhenotypes[r][c];
                if (phen in uniqueDict) {
                    uniqueDict[phen] +=1;
                } else {
                    uniqueDict[phen] = 1;
                }

            }
        }

        var uniqueArray = []
        for (var key in uniqueDict) {
            uniqueArray.push({'phen': key, 'count': uniqueDict[key]})
        }

        uniqueArray.sort(function(a,b){ //Array now becomes [7, 8, 25, 41]
            return b['count'] - a['count']
        });

        return uniqueArray;
    }


    possiblePhenotypes() {
        var offspringPhenotypes = [];
        var possibleGenotypes = this.possibleOffspring();
        for (var r = 0; r < possibleGenotypes.length;++r) {
            var rowPhenotypes = [];

            for (var c = 0; c < possibleGenotypes[r].length;++c) {
                var gen = possibleGenotypes[r][c];
                var phen = genToPhen(gen);
                rowPhenotypes.push(phen);
            }
            offspringPhenotypes.push(rowPhenotypes);
        }
        return offspringPhenotypes;
    }

    uniqueGenotypes() {
        var unique= [];

        var uniqueDict = {}
        var possGenotypes = this.possibleOffspring();
        for (var r = 0; r < possGenotypes.length;++r) {
            for (var c = 0; c < possGenotypes[r].length; ++c) {
                var gen = possGenotypes[r][c];
                if (gen in uniqueDict) {
                    uniqueDict[gen] +=1;
                } else {
                    uniqueDict[gen] = 1;
                }

            }
        }

        var uniqueArray = []
        for (var key in uniqueDict) {
            uniqueArray.push({'gen': key, 'count': uniqueDict[key]})
        }

        uniqueArray.sort(function(a,b){ //Array now becomes [7, 8, 25, 41]
            return b['count'] - a['count']
        });

        return uniqueArray;
    }


    possibleOffspring() {
        var femaleGametes = this.femaleGametes();
        var maleGametes = this.maleGametes();

        var offspringGenotypes = [];

        for (var r = 0; r < femaleGametes.length; ++r) {

            var rowGenotypes = [];
            for (var c = 0; c < maleGametes.length; ++c) {
                rowGenotypes.push(this.combine(femaleGametes[r], maleGametes[c]));
            }
            offspringGenotypes.push(rowGenotypes);

        }
        return offspringGenotypes;
    }

    numSquares() {
        return this.maleGametes().length * this.femaleGametes().length;
    }
}

PunnettSquare.InheritanceAutosomal = 1;
PunnettSquare.InheritanceXLinked = 2;
