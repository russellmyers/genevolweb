// Event Listeners

function showGenotypeButClicked(e) {
    var showBut = e.target;

    pd.showGenotypes = !(pd.showGenotypes);

    showGenotypesChanged();

}


function inhPatternSelected(e) {
    var el = e.target;

    var tickEl = document.getElementById("tick-img");
    var showBut = document.getElementById("show-but");

    var selectedOption = el.options[el.selectedIndex].value;

    if (selectedOption == "-1") {
        pd.inhTypeToShow = null;
    }
    else {
        pd.inhTypeToShow = selectedOption;
    }

    if (selectedOption == "-1") {
        //tickEl.style.display = "none";
        //showBut.style.display = "none";
        pd.inhTypeToShow = null;
        //showGenotypes = true;
    }
    else {
        //tickEl.style.display = "block";
        pd.inhTypeToShow = selectedOption;
        //showGenotypes= true;
    }

    inhTypeToShowChanged();

    // if (selectedOption in consistentPerInferrer) {
    //     if (consistentPerInferrer[selectedOption] == 0) {
    //         tickEl.src = staticPrefix + "img/cross.PNG";
    //         showBut.style.display = "none";
    //         pd.showGenotypes = false;
    //
    //     }
    //
    //     else {
    //         tickEl.src = staticPrefix + "img/tick.jpg";
    //         showBut.style.display = "block";
    //     }
    //
    // }
    // else {
    //         tickEl.src = staticPrefix + "img/cross.PNG";
    //         showBut.style.display = "none";
    //         pd.showGenotypes = false;
    // }
    //
    // showGenotypesChanged();

    //alert("yeah " + selectedOption + " " + consistentPerInferrer.toString());

}

function getRelPos(e) {
  var targetEl = e.target;
  var rect = targetEl.getBoundingClientRect();
  posX = e.clientX - rect.left;
  posY = e.clientY - rect.top;
  return {'x':posX, 'y':posY};

}

function logEvent(e, text) {
    text = text || '*';
    var relPos = getRelPos(e);

    console.log(e.target.id + ' ' + text + ' x: ' + relPos.x + ' y: ' + relPos.y);

}

function canvasMouseDown(e) {
     canvDrag.isDragging = false;

     if (pd.inhTypeToShow == null)  {
         return;
     }

     var pos = getRelPos(e);

     var gCell = pd.pointInGenCells(pos);
     var txt = (gCell == null) ? ' No gen cell selected' : gCell.text;
     logEvent(e, 'Mouse down ' + txt);

     if (gCell == null) {
         return;
     }

     canvDrag.isDragging = true;
     canvDrag.prevMousePos = pos;
     pd.addDraggingCell(pos, gCell.text);

     pd.drawStuff();

}

function canvasMouseMove(e) {

   pos = getRelPos(e);

   if (canvDrag.isDragging) {

      logEvent(e, 'Mouse move');
      var dx = pos.x - canvDrag.prevMousePos.x;
      var dy = pos.y - canvDrag.prevMousePos.y;
      logEvent(e, ' Move delta: ' + dx + ' ' + dy );
      canvDrag.prevMousePos = pos;
      if (pd._draggingCell == null) {
      }
      else {
      	pd._draggingCell.pos.x  += dx;
      	pd._draggingCell.pos.y += dy;
      }

      var overCell = pd.pointInOrgCells(pos);
      var txt = 'None';
      if (!(overCell == null)) {
          txt = overCell.org.id;
          //overCell.cellSize = {'w': 50, 'h':50};
      }

      if (overCell == null) {
          if ( !(canvDrag.overOrgCell == null) ) {
              // exiting
              logEvent(e, 'Exiting: ' + canvDrag.overOrgCell.org.id);
              canvDrag.overOrgCell.shrink();
              canvDrag.overOrgCell = null;
              pd._draggingCell.textFillStyle = 'black';
          }
      }
      else {
          if (canvDrag.overOrgCell == null) {
              // entering
              logEvent(e, 'Entering: ' + overCell.org.id);
              canvDrag.overOrgCell = overCell;
              pd._draggingCell.textFillStyle = (overCell.org.afflicted) ? 'white' : 'black';
              overCell.superSize();
          }
          else if (canvDrag.overOrgCell == overCell) {
              // still in
              logEvent(e, 'Still in: ' + overCell.org.id);
          }
      }

      //logEvent(e, 'Over: ' + txt);
      pd.drawStuff();

   }

  var overGenCell = pd.pointInGenCells(pos);

  if (overGenCell == null) {
      if ( !(canvDrag.overGenCell == null) ) {
          // exiting
          logEvent(e, 'Exiting: ' + canvDrag.overGenCell.text);
          canvDrag.overGenCell.shrink();
          canvDrag.overGenCell = null;
          pd.drawStuff();

      }
  }
  else {
      if (canvDrag.overGenCell == null) {
          // entering
          logEvent(e, 'Entering: ' + overGenCell.text);
          canvDrag.overGenCell = overGenCell;
          overGenCell.superSize();
          pd.drawStuff();
      }
      else if (canvDrag.overGenCell == overGenCell) {
          // still in
          logEvent(e, 'Still in: ' + overGenCell.text);
      }
  }


}

function canvasMouseUp(e) {


   if (!canvDrag.isDragging) {
       return;
   }

   pos = getRelPos(e);
   logEvent(e, ' Mouse up: ');

   if (pd._draggingCell == null)  {
   }
   else {
     if (canvDrag.overOrgCell == null) {

     }
     else {
         // dropping
         canvDrag.overOrgCell.proposedText = pd._draggingCell.text;
     }

      canvDrag.isDragging = false;
      canvDrag.prevMousePos = null;
      canvDrag.overOrgCell = null;
      pd.removeDraggingCell();

      pd.drawStuff();

   }

}