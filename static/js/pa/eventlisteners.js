// Event Listeners

function showGenotypeButClicked(e) {
    var showBut = e.target;


    showGenotypes = !(showGenotypes);

    if (showGenotypes) {
        showBut.innerHTML = 'Hide Inferrable Genotypes';
    }
    else {
        showBut.innerHTML = 'Reveal Inferrable Genotypes';
    }

    pd.showGenotypes = showGenotypes;

    pd.drawStuff();
}


function inhPatternSelected(e) {
    var el = e.target;

    var tickEl = document.getElementById("tick-img");
    var showBut = document.getElementById("show-but");

    var selectedOption = el.options[el.selectedIndex].value;

    if (selectedOption == "-1") {
        tickEl.style.display = "none";
        showBut.style.display = "none";
        pd.inhTypeToShow = null;
        pd.showGenotypes = true;
    }
    else {
        tickEl.style.display = "block";
        pd.inhTypeToShow = selectedOption;
        pd.showGenotypes= true;
    }
    if (selectedOption in consistentPerInferrer) {
        if (consistentPerInferrer[selectedOption] == 0) {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";

        }

        else {
            tickEl.src = staticPrefix + "img/tick.jpg";
            showBut.style.display = "block";
        }

    }
    else {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
    }
    //alert("yeah " + selectedOption + " " + consistentPerInferrer.toString());

}