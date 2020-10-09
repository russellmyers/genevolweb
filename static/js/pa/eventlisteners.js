// Event Listeners

function showGenotypeButClicked(e) {
    var showBut = e.target;

    showGenotypes = !(showGenotypes);

    showGenotypesChanged();

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
        //showGenotypes = true;
    }
    else {
        tickEl.style.display = "block";
        pd.inhTypeToShow = selectedOption;
        //showGenotypes= true;
    }



    if (selectedOption in consistentPerInferrer) {
        if (consistentPerInferrer[selectedOption] == 0) {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
            showGenotypes = false;

        }

        else {
            tickEl.src = staticPrefix + "img/tick.jpg";
            showBut.style.display = "block";
        }

    }
    else {
            tickEl.src = staticPrefix + "img/cross.PNG";
            showBut.style.display = "none";
            showGenotypes = false;
    }

    showGenotypesChanged();

    //alert("yeah " + selectedOption + " " + consistentPerInferrer.toString());

}

function logEvent(e, text) {
    text = text || '*';
    var targ = e.target;
    var rect = targ.getBoundingClientRect();
    posX = e.clientX - rect.left;
    posY = e.clientY - rect.top;

    console.log(e.target.id + ' ' + text + ' x: ' + posX + ' y: ' + posY);

}

function canvasMouseDown(e) {

     var doSomething = false;
     if (!(pd.inhTypeToShow == null)) {
         doSomething = true;
     }
     logEvent(e, 'Mouse down ' + doSomething);

     if (!doSomething) {
         return;
     }


}