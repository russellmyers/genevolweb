// Event Listeners

function genPhenSelected(e) {
       el = e.target;
       val = el.value;

       genPhen = val;
       genPhenChanged();

}

function orgTypeSelected(e) {
    //alert("oh I see " + e.target.id);
    el = e.target;

    if (el.name == "p1") {
        p1Ind = parseInt(el.value)-1;
    }
    else {
        p2Ind= parseInt(el.value)-1;
    }

    orgTypeChanged();



}

function crossTypeSelected(e) {
    el = e.target;
    val = el.value;
    var p1_val;
    var p2_val;

    switch (val) {
        case '1':
            p1_val = 0;
            p2_val = 2;
            break;
        case '2':
            p1_val = 1;
            p2_val = 2;
            break;
        case '3':
            p1_val = 1;
            p2_val = 1;
            break;
        default:
            p1_val = 0;
            p2_val = 0;
            break;

    }

    p1Ind = p1_val;
    p2Ind = p2_val;
    crossTypeChanged();

 }

function numTraitsSelected(e) {
    el = e.target;
    val = el.value;
    switch (val) {
        case '1':
            numTraits = 1;
            break;
        case '2':
            numTraits = 2;
            break;
        case '3':
            numTraits= 3;
            break;
        default:
            numTraits = 1;
            break;

    }
    numTraitsChanged();

}

function crossButClicked(e) {
    var crossBut = e.target;

    switch (state) {
        case 1:
            state = 2;
            break;

        case 2:
            state = 3;
            break;

        case 3:
            state = 1;
            break;

        default:
            state = 3;
            break;
    }

    stateChanged();

}

