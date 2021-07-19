
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
    var showNumFoundDiv = document.getElementById("tot-found-div");

    if (pd.inhTypeToShow == null) {
        tickEl.style.display = "none";
        showBut.style.display = "none";
        selected_option = "-1";
        pd.createGenCells([]);
        showNumFoundDiv.style.display = "none";
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
            pd.createGenCells([]);
            showNumFoundDiv.style.display = "none";
            var audioEl = document.getElementById('myAudio2');
            audioEl.pause();
            audioEl.currentTime = 0;
            audioEl.play();

        }

        else {
            tickEl.src = staticPrefix + "img/tick.jpg";
            showBut.style.display = "block";
            pd.createGenCells(possGensPerInferrer[selectedOption]);
            proposedTextsChanged(selectedOption);
            showNumFoundDiv.style.display = "block";
            var audioEl = document.getElementById('myAudio');
            audioEl.pause();
            audioEl.currentTime = 0;
            audioEl.play();
        }

    }
    else {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
            pd.showGenotypes = false;
            pd.createGenCells([]);
            showNumFoundDiv.style.display = "none";
            var audioEl = document.getElementById('myAudio2');
            audioEl.pause();
            audioEl.currentTime = 0;
            audioEl.play();
    }

    showGenotypesChanged();

}

function proposedTextsChanged(inhType) {
        var totNumInferrableEl = document.getElementById('tot-num');
        var numFoundEl = document.getElementById('num-correct');

        totNumInferrableEl.innerHTML = '' + pedigree.numInferrable(inhType);


        var numCorrect = 0;
        for (var i = 0;i < pd._orgPairCells.length; ++ i) {
            var orgPairCell = pd._orgPairCells[i];
            for (var j = 0; j < orgPairCell._orgCells.length;++j) {
                var orgCell = orgPairCell._orgCells[j];
                if (orgCell.correctGuess(exclUninferrables=true)) {
                    numCorrect +=1;
                }
            }
        }

        if (numCorrect >= pedigree.numInferrable(inhType) ) {
            var audioEl = document.getElementById('myAudio3');
            audioEl.pause();
            audioEl.currentTime = 0;
            audioEl.play();
            var uninferrables = {'AR': 'A-', 'AD': '-a', 'XR': 'XAX-', 'XD': 'X-Xa', 'YR': 'X-Y'}
            for (var i = 0;i < pd._orgPairCells.length; ++ i) {
                var orgPairCell = pd._orgPairCells[i];
                for (var j = 0; j < orgPairCell._orgCells.length;++j) {
                     var orgCell = orgPairCell._orgCells[j];
                     if (orgCell.proposedTexts[inhType] == null) {
                         orgCell.proposedTexts[inhType] = uninferrables[inhType];
                     }
                 }
            }

        }
        numFoundEl.innerHTML = '' + numCorrect;




}