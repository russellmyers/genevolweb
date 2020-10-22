// Model classes

class Pedigree {

    constructor(pedJson, name = 'Pedigree') {
        this.orgs = pedJson.orgs;
        this.adam = pedJson.adam;
        this.name = name;
        this.actual = pedJson.actual;
        this.consistent = pedJson.consistent;
    }

    orgWithId(id) {
        for (var i = 0; i < this.orgs.length;++i) {
            var org = this.orgs[i];
            if (org.id  == id) {
                return org;
            }
        }
        return null;
    }

    numInferrable(inhType) {
        var num = 0;
        for (var i = 0; i < this.orgs.length;++i) {
            if (this.orgs[i].inferrable_genotypes[inhType] == null) {

            }
            else {
                num +=1;
            }
        }
        return num;
    }

    get orgPairs() {
        var pairs = [];
        for (var i = 0;i < this.orgs.length;++i) {
            var pair = [];
            var org = this.orgs[i];
            if ((org.isInlaw) || ((org.level == 1) && (org.id != this.adam)) ) {

            }
            else {
                pair.push(org);
                if (org.partner == null) {
                    pair.push(null);
                }
                else {
                    pair.push(this.orgWithId(org.partner));
                }
                pairs.push(pair);
            }



        }
        return pairs;
    }

    getChildOrgPairs(orgPair) {
        var org = orgPair[0];
        var childPairs = [];
        for (var i = 0; i < org.children.length;++i) {
            var child = this.orgWithId(org.children[i]);
            var pair = [];
            pair.push(child);
            if (child.partner == null) {
                pair.push(null);
            }
            else {
                pair.push(this.orgWithId(child.partner));
            }
            childPairs.push(pair);

        }
        return childPairs;
    }

}
