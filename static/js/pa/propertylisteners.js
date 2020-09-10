
// Property change listener functions

function showGenotypesChanged() {

    var showBut = document.getElementById('show-but');

    if (showGenotypes) {
        showBut.innerHTML = 'Hide Inferrable Genotypes';
    }
    else {
        showBut.innerHTML = 'Reveal Inferrable Genotypes';
    }

    pd.showGenotypes = showGenotypes;

    pd.drawStuff();


}
