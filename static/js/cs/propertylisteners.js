
// Property change listener functions

function stateChanged() {
    var crossBut = document.getElementById("cross");

    switch (state) {
        case 1:
            crossBut.innerHTML = 'Meiosis';
            break;

        case 2:
            crossBut.innerHTML = 'Cross';
            break;

        case 3:
            crossBut.innerHTML  = 'Clear';
            break;

        default:
            crossBut.innerHTML = 'Cross';
            break;
    }

    psd.state = state;

    psd.drawStuff();

    rt.setState(state);

}

function ratioRowChanged() {
    //alert('row changed');
    var table = document.getElementById("ratio-table");
    for (var i = 0, row; row = table.rows[i]; ++i) {
        row.classList.remove('ratio-row-selected');
        if (ratioRow == null){

        }
        else {
            if (row.rowIndex == ratioRow) {
                row.classList.add('ratio-row-selected');
            }
        }
    }

    if (ratioRow == null) {
        psd.drawStuff();
        return;
    }


    if (ps.genPhen == 'g') {
        var unique = ps.uniqueGenotypes();
        var gen = unique[ratioRow - 1].gen;
        psd.drawStuff(gen);
    } else {
        var unique = ps.uniquePhenotypes();
        var phen = unique[ratioRow - 1].phen;
        psd.drawStuff(phen);
    }
}

function crossTypeChanged() {


    for (i = 0; i < 3; ++i) {
        el1 = document.getElementById("id_p1_" + i);
        if (i == p1Ind) {
            el1.parentElement.parentElement.classList.add('active');
        } else {
            el1.parentElement.parentElement.classList.remove('active');
        }

        el2 = document.getElementById("id_p2_" + i);
        if (i == p2Ind) {
            el2.parentElement.parentElement.classList.add('active');
        } else {
            el2.parentElement.parentElement.classList.remove('active');
        }
    }

    orgTypeChanged();

}
function orgTypeChanged() {
    var orgs = JSON.parse(document.getElementById('jOrgs').textContent);

    var formattedGameteFreqsP1 = [];
    for (var i=0;i <possGametesRolledUp[numTraits-1][p1Ind].length;++i ) {
        formattedGameteFreqsP1.push(possGametesRolledUp[numTraits-1][p1Ind][i][0] + ' ' + possGametesRolledUp[numTraits-1][p1Ind][i][2]  + ' / ' + possGametesRolledUp[numTraits-1][p1Ind][i][3] );
    }
    var formattedGameteFreqsP2 = [];
    for (var i=0;i <possGametesRolledUp[numTraits-1][p2Ind].length;++i ) {
        formattedGameteFreqsP2.push(possGametesRolledUp[numTraits-1][p2Ind][i][0] + ' ' + possGametesRolledUp[numTraits-1][p2Ind][i][2]  + ' / ' + possGametesRolledUp[numTraits-1][p2Ind][i][3] );
    }
    formattedGameteFreqsP1 =  formattedGameteFreqsP1.join('\n');
    formattedGameteFreqsP2 =  formattedGameteFreqsP2.join('\n');

    document.getElementById("p1" + "_img").src = staticPrefix + "img/" + genomeName + "/"+ genomeName + "_" + orgs[numTraits-1][p1Ind].phen + ".png";
    document.getElementById("p1" + "_img").title = "Phase:\n" + orgs[numTraits-1][p1Ind].gen_phase + "\n\nExpected gamete frequencies:\n" + formattedGameteFreqsP1;
    document.getElementById("p1" + "_gen").innerText = orgs[numTraits-1][p1Ind].gen;
    document.getElementById("p2" + "_img").src = staticPrefix + "img/" + genomeName + "/" + genomeName + "_" + orgs[numTraits-1][p2Ind].phen + ".png";
    document.getElementById("p2" + "_img").title = "Phase:\n" + orgs[numTraits-1][p2Ind].gen_phase + "\n\nExpected gamete frequencies:\n" + formattedGameteFreqsP2;
    document.getElementById("p2" + "_gen").innerText = orgs[numTraits-1][p2Ind].gen;

    changeCrossType();

    setPunnettSquare();


}


function genPhenChanged() {

      setPunnettSquare();

}

function numTraitsChanged(first) {

      first = first || false;

     var crossTypeEl = document.getElementById('id_cross_type');
     var hybridOptions = ['Monohybrid Cross', 'Dihybrid Cross', 'TriHybrid Cross']
     crossTypeEl.options[2].innerHTML = hybridOptions[numTraits - 1];

     var phenDescriptionsEl = document.getElementById('phen-descriptions');
     var phenDescriptionTexts = [document.getElementById('jPhenDescriptions1'), document.getElementById('jPhenDescriptions2'), document.getElementById('jPhenDescriptions3')];
     phenDescriptionsEl.innerHTML = ''
     for (i=0;i < numTraits; ++i) {
         phenDescriptionsEl.innerHTML += phenDescriptionTexts[i].innerText.replace(/"/g, '');
         phenDescriptionsEl.innerHTML += '<BR>';
     }

      orgTypeChanged();
      setPunnettSquare();

}
