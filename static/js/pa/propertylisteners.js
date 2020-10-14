
// Property change listener functions

function showGenotypesChanged() {

    var showBut = document.getElementById('show-but');

    if (pd.showGenotypes) {
        showBut.innerHTML = 'Hide Inferrable Genotypes';
    }
    else {
        showBut.innerHTML = 'Reveal Inferrable Genotypes';
    }

    //pd.showGenotypes = showGenotypes;

    pd.drawStuff();


}

function inhTypeToShowChanged() {

    var tickEl = document.getElementById("tick-img");
    var showBut = document.getElementById("show-but");

    if (pd.inhTypeToShow == null) {
        tickEl.style.display = "none";
        showBut.style.display = "none";
        selected_option = "-1";
        pd.createGenCells([])
    }
    else {
        tickEl.style.display = "block";
        selectedOption = pd.inhTypeToShow;
    }

    if (selectedOption in consistentPerInferrer) {
        if (consistentPerInferrer[selectedOption] == 0) {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
            pd.showGenotypes = false;
            pd.createGenCells([])

        }

        else {
            tickEl.src = staticPrefix + "img/tick.jpg";
            showBut.style.display = "block";
            pd.createGenCells(possGensPerInferrer[selectedOption])
        }

    }
    else {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
            pd.showGenotypes = false;
            pd.createGenCells([]);
    }

    showGenotypesChanged();

}
