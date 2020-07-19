// View Classes

class Dimension {
    constructor(w,h) {
        this.w = w;
        this.h = h;
    }
}

class Point {
    constructor(x,y) {
        this.x = x;
        this.y = y;
    }
}


class PunnettCell {
    constructor(parent, r, c) {
        this.parent = parent;
        this.r = r;
        this.c = c;
        this.img = null;
        if (this.parent.punnettSquare.genPhen == 'p') {
           this.loadPhenImage();
        }


    }

    loadPhenImage() {
       var cellPhenotypes = this.parent.punnettSquare.possiblePhenotypes();
       var phen = cellPhenotypes[this.r][this.c];
       this.img = this.parent.phenImageDict[phen];
       //x = 1;
    }

    get cellSize() {
        return new Dimension(this.parent.colWidth, this.parent.rowHeight);
    }

    get cellPosition() {
        return new Point(this.parent.padding.l + this.cellSize.w * (this.c + 1), this.parent.padding.t + this.cellSize.h * (this.r + 1));
    }

    isPointInCell(p) {
        if ((p.x >= this.cellPosition.x) && (p.x <= this.cellPosition.x + this.cellSize.w) && (p.y >= this.cellPosition.y) &&  (p.y <= this.cellPosition.y + this.cellSize.h)) {
            return true;
        }
        return false;
    }

    draw(alpha) {

        alpha = alpha || 1.0;

        this.parent.ctx.save();

        this.parent.ctx.clearRect(this.cellPosition.x+2,this.cellPosition.y+2,this.cellSize.w-4,this.cellSize.h-4);

        if (this.parent.state == PunnettSquareDiv.StateFertilised) {
            var svdFillStyle = this.parent.ctx.fillStyle;
            var cellGenotypes = this.parent.punnettSquare.possibleOffspring();
            var cPos = this.cellPosition;
            var cSize = this.cellSize;
            var svdFont = this.parent.ctx.font;
            if (this.parent.punnettSquare.genPhen == 'g') {
                this.parent.setGameteFontSize(cellGenotypes[0][0], cSize.w, [25, 22, 19, 16, 13, 10, 7]);
                this.parent.ctx.fillStyle = "rgba(0, 0, 0, " + alpha + ")";
                this.parent.ctx.fillText(cellGenotypes[this.r][this.c], cPos.x, cPos.y + cSize.h - this.parent.textLift);
                this.parent.font = svdFont;
            }
            else {
                 var size = cSize.h;
                  var offset = 0;
                  if (this.parent.punnettSquare.genomeName == 'pea') {
                      size*=0.8;
                      offset = 2;
                  }
                  this.parent.ctx.globalAlpha = alpha;
                  this.parent.ctx.drawImage(this.img,cPos.x + offset, cPos.y + offset, size, size); // Or at whatever offset you like#}
            }

            if (this.parent.highlightedCell == null) {
            }
            else {
                    if ((this.r == this.parent.highlightedCell.r) && (this.c == this.parent.highlightedCell.c)) {
                        this.parent.ctx.strokeStyle = "blue";
                        this.parent.ctx.strokeRect(cPos.x + 1, cPos.y + 1, cSize.w - 2, cSize.h - 2);
                    }
            }


            this.parent.ctx.fillStyle = svdFillStyle;


        }
        this.parent.ctx.restore();
    }


}

class PunnettSquareDiv {
   // static StateHidden = 1;
   // static StateMeiosis = 2;
   // static StateFertilised = 3;

  constructor(punnettSquare, canvasEl,state, cellZoom, staticPrefix, padding) {
    this.punnettSquare = punnettSquare;
    this.canvasEl = canvasEl;
    this.ctx = this.canvasEl.getContext('2d');
    this.padding = padding ||  {'t':10, 'b': 10, 'l': 10, 'r': 10}
    this.textLift = 3;
    this.highlightedCell = null;
    this.state = state || PunnettSquareDiv.StateHidden;
    this.cellZoom = cellZoom;
    this.staticPrefix = staticPrefix;

    this.phenImageDict = this.loadPhenImages();


    var self = this;

    this.canvasEl.onmousemove =  function(e) {

        if (self.state == PunnettSquareDiv.StateFertilised) {

        }
        else {
            return;
        }
         // Get the current mouse position
         var r = self.canvasEl.getBoundingClientRect();
         var x = e.clientX - r.left, y = e.clientY - r.top;

        var svdFillStyle = self.ctx.fillStyle;

        var newHighlightedCell = null;

         for (var i = 0;i < self.punnettCells.length; ++i) {
             var cell = self.punnettCells[i];


             if (cell.isPointInCell(new Point(x,y))) {
                    newHighlightedCell = cell;
                    if ( (self.highlightedCell == null) || (self.highlightedCell != cell)) {
                        self.highlightedCell = cell;
                        self.drawStuff();
                        break;
                    }
             }



         }

         if ((self.highlightedCell != null) && (newHighlightedCell == null))  {
             self.highlightedCell = null;
             self.drawStuff(); // moved out of punnet square - nothing
         }

         self.ctx.fillStyle = svdFillStyle;

    };

    this.punnettCells = this.createPunnettCells();

  }

  loadPhenImages() {

      var imgDict = {}
      var unique = this.punnettSquare.uniquePhenotypes();
      for (i=0;i < unique.length; ++i) {
           var phen = unique[i]['phen'];
           var phenImgName = this.staticPrefix + "img/" + this.punnettSquare.genomeName + '/' +  this.punnettSquare.genomeName + '_' + phen + ".png";
           var img = new Image;
           var svdThis = this;
           img.onload = function(){
            //svdThis.parent.ctx.drawImage(svdThis.img,cPos.x, cPos.y, cSize.h, cSize.h); // Or at whatever offset you like
           };
           img.src = phenImgName;
           imgDict[phen] =  img;
      }

      return imgDict;
   }

  showCellZoom(numSameGen, totNumGen, numSamePhen, totNumPhen) {
        if (this.highlightedCell == null) {
            this.cellZoom.style.display = "none";
        }
        else {
            this.cellZoom.style.display = "block";
            var children = this.cellZoom.children;
            for (var i = 0;i < children.length;++i) {
                if (children[i].id == 'zoom-image') {
                    var zoomImageEl = children[i];

                    if (this.punnettSquare.genPhen == 'p') {

                        var possibleGenotypes = this.punnettSquare.possibleOffspring();
                        var highlightedCellGenotype = possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c];

                        zoomImageEl.src =  this.staticPrefix + "img/" + this.punnettSquare.genomeName + '/' +  this.punnettSquare.genomeName + '_' + genToPhen(possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c]) + ".png";
                        if (this.punnettSquare.genomeName == 'pea') {
                            zoomImageEl.style.width = '100px';
                        }
                        else {
                            zoomImageEl.style.width = '150px';
                        }
                        zoomImageEl.style.display = "block";
                    }
                    else {
                        zoomImageEl.style.display = "none";
                    }
                }
                if (children[i].id == 'zoom-genotype') {
                    var zoomGenotypeEl = children[i];
                    if (this.punnettSquare.genPhen == 'g') {

                        var possibleGenotypes = this.punnettSquare.possibleOffspring();
                        var highlightedCellGenotype = possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c];
                        zoomGenotypeEl.innerHTML = highlightedCellGenotype;
                        zoomGenotypeEl.style.display = "block";
                    } else {
                        zoomGenotypeEl.style.display = "none";
                    }
                }
                if (children[i].id == 'zoom-gen') {
                    var zoomGenotypeEl = children[i];
                    var possibleGenotypes = this.punnettSquare.possibleOffspring();
                    var highlightedCellGenotype = possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c];
                    if (this.punnettSquare.genPhen == 'p') {
                        zoomGenotypeEl.innerHTML = highlightedCellGenotype;
                    }
                    else {
                        zoomGenotypeEl.innerHTML = '';
                    }
                }


                if (children[i].id == 'num-same') {
                    children[i].innerHTML = numSameGen;
                }
                 if (children[i].id == 'tot-num') {
                    children[i].innerHTML = totNumGen;
                }

                if (children[i].id == 'num-same-phen') {
                    children[i].innerHTML = numSamePhen;
                }
                 if (children[i].id == 'tot-num-phen') {
                    children[i].innerHTML = totNumPhen;
                }

            x = 1;
           }
        }


  }

  createPunnettCells() {

      var punnettCells = [];

      for (var r = 0; r < this.numRows -1; ++r) {
          for (var c =0; c < this.numCols -1; ++c) {
              punnettCells.push(new PunnettCell(this, r, c));
          }
      }

      return punnettCells;
  }



  get canvasSize() {
      const { width, height } = this.canvasEl.getBoundingClientRect();
      return {'w': width, 'h': height}
  }

  get numRows() {
      return Math.pow(2, this.punnettSquare.getNumTraits()) + 1;
  }

  get numCols() {
      return Math.pow(2, this.punnettSquare.getNumTraits()) + 1;
  }

  get rowHeight() {
      var size = this.canvasSize;
      var height =  (size.h - this.padding.t - this.padding.b) / this.numRows;
      return height;

  }

  get colWidth() {
      var size = this.canvasSize;
      var width =  (size.w - this.padding.l - this.padding.r) / this.numCols;
      return width;
  }


  drawLine(st, end, lineWidth) {

    var svdLineWidth = this.ctx.lineWidth;
    this.ctx.lineWidth =  lineWidth || 1;

    this.ctx.moveTo(st.x, st.y);
    this.ctx.lineTo(end.x, end.y);
    this.ctx.stroke();
    this.ctx.lineWidth = svdLineWidth;

  }

  drawRowLines()  {

      var y = this.padding.t+ this.rowHeight;

      for (var i = 0; i < this.numRows;++i) {
          var lineWidth = 1;
          if (i == 0) {
              lineWidth = 2;
          }
          if ((i> 0) && (this.state == PunnettSquareDiv.StateMeiosis)) {
            this.drawLine(new Point(this.padding.l,y), new Point(this.padding.l + this.colWidth, y)); //, lineWidth);
          }
          else {
            this.drawLine(new Point(this.padding.l,y), new Point(this.canvasSize.w - this.padding.r, y)); //, lineWidth);
          }
          y = y + this.rowHeight;
      }

  }

  drawColLines() {
      var x = this.padding.l + this.colWidth;

      for (var i = 0; i < this.numCols;++i) {
          var lineWidth = 1;
          if (i == 0) {
              lineWidth = 2;
          }
          if ((i > 0) && (this.state == PunnettSquareDiv.StateMeiosis)) {
              this.drawLine(new Point(x, this.padding.t), new Point(x, this.padding.t + this.rowHeight)); //, lineWidth);
          }
          else {
              this.drawLine(new Point(x, this.padding.t), new Point(x, this.canvasSize.h - this.padding.b)); //, lineWidth);
          }
          x = x + this.colWidth;
      }
  }

  drawTopCorner() {
      var imgWidth = 20;
      var imgHeight = 20;
       var femaleImg = document.getElementById("gender-female-image");
       this.ctx.drawImage(femaleImg, this.padding.l, this.padding.t + this.rowHeight - imgHeight, imgWidth, imgHeight);
       var maleImg = document.getElementById("gender-male-image");
       this.ctx.drawImage(maleImg, this.padding.l + this.colWidth - imgWidth, this.padding.t, imgWidth, imgHeight);

  }

  drawCellsGenotype() {
      var higlightedCellGenotype = null;
      var highlightedCellPhenotype = null;

      var numSameGen = 0;
      var totNumGen = this.punnettCells.length;
      var numSamePhen = 0;
      var totNumPhen = this.punnettCells.length;


      if (this.highlightedCell == null) {
      }
      else {
        var possibleGenotypes = this.punnettSquare.possibleOffspring();
        var highlightedCellGenotype = possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c];
        highlightedCellPhenotype = genToPhen(highlightedCellGenotype);
      }

      for (var i = 0;i < this.punnettCells.length; ++i) {
          var cell = this.punnettCells[i];
          if (highlightedCellGenotype == null) {
              cell.draw();
          }
          else {
             if (highlightedCellGenotype == possibleGenotypes[cell.r][cell.c]) {
                cell.draw();
                numSameGen+=1;
             }
             else {
                 cell.draw(0.4);
             }
          }
      }

     for (var i = 0;i < this.punnettCells.length; ++i) {
          var cell = this.punnettCells[i];
          if (highlightedCellPhenotype == null) {

          }
          else {
             if (highlightedCellPhenotype == genToPhen(possibleGenotypes[cell.r][cell.c])) {

                numSamePhen+=1;
             }
             else {

             }
          }
      }


      this.showCellZoom(numSameGen, totNumGen, numSamePhen, totNumPhen);



  }

  highlightCellsWithGenotype(gen) {
     var possibleGenotypes = this.punnettSquare.possibleOffspring();
     for (var i = 0;i < this.punnettCells.length; ++i) {
         var cell = this.punnettCells[i];
         if (gen == possibleGenotypes[cell.r][cell.c]) {
             cell.draw();
         } else {
             cell.draw(0.4);
         }

      }
  }

  highlightCellsWithPhenotype(phen) {
     var possibleGenotypes = this.punnettSquare.possibleOffspring();
     for (var i = 0;i < this.punnettCells.length; ++i) {
         var cell = this.punnettCells[i];
         if (phen == genToPhen(possibleGenotypes[cell.r][cell.c])) {
             cell.draw();
         } else {
            // alert('Not highlighting: '+ cell.r + ' ' + cell.c);
             cell.draw(0.4);
         }

      }

  }

  highlightCellsWithOverride(highlightOverride) {
       if (this.punnettSquare.genPhen == 'g') {
           this.highlightCellsWithGenotype(highlightOverride);
       }
       else {
           this.highlightCellsWithPhenotype(highlightOverride);
       }

  }

  drawCellsPhenotype() {
      var highlightedCellPhenotype = null;

      if (this.highlightedCell == null) {
      }
      else {
        var possibleGenotypes = this.punnettSquare.possibleOffspring();
        var highlightedCellGenotype = possibleGenotypes[this.highlightedCell.r][this.highlightedCell.c];
        highlightedCellPhenotype = genToPhen(highlightedCellGenotype);
      }

      var numSameGen = 0;
      var totNumGen = this.punnettCells.length;
      var numSamePhen = 0;
      var totNumPhen = this.punnettCells.length;


      for (var i = 0;i < this.punnettCells.length; ++i) {
          var cell = this.punnettCells[i];
          if (highlightedCellGenotype == null) {
              cell.draw();
          }
          else {
             if (highlightedCellPhenotype == genToPhen(possibleGenotypes[cell.r][cell.c])) {
                cell.draw();
                numSamePhen+=1;
             }
             else {
                 cell.draw(0.4);
             }
          }
      }

     for (var i = 0;i < this.punnettCells.length; ++i) {
          var cell = this.punnettCells[i];
          if (highlightedCellGenotype == null) {

          }
          else {
             if (highlightedCellGenotype == possibleGenotypes[cell.r][cell.c]) {
                numSameGen+=1;
             }
             else {
             }
          }
      }

      this.showCellZoom(numSameGen, totNumGen, numSamePhen, totNumPhen);



  }

  drawCells() {

       if (this.punnettSquare.genPhen == 'g') {
           this.drawCellsGenotype();
       }
       else {
            this.drawCellsPhenotype();
       }



  }

  setFontSize(size, bold) {
      bold = bold || false;

      if (bold) {
          this.ctx.font = "bold " + size + "px Helvetica Neue";
      }
      else {
          this.ctx.font =  size + "px Helvetica Neue";
      }
  }

  setGameteFontSize(gamete, maxWidth, trySizes) {

      trySizes = trySizes || [16, 12, 9]

      for (var i = 0; i < trySizes.length; ++i) {
          var fontSize = trySizes[i];
          this.setFontSize(fontSize); //this.ctx.font = "16px Helvetica Neue";
          var textWidth = this.ctx.measureText(gamete).width;
          if (textWidth < maxWidth) {
              break;
          }
      }


      return fontSize;

  }

  possibleGameteSizes() {
        var numTraits = this.punnettSquare.getNumTraits();
        var possSizes = [];
        switch (numTraits) {
            case 1:
                possSizes = [25,20,15];
                break;
            case 2:
                possSizes = [20, 15, 10];
                break;
            case 3:
                possSizes = [16, 12, 9];
                break;
            default:
                possSizes = [16, 12, 9];
        }

        return possSizes;

  }

  gameteFractionFontOffset() {
        var numTraits = this.punnettSquare.getNumTraits();
        var offset = 0;
        switch (numTraits) {
            case 1:
                offset = 10;
                break;
            case 2:
                offset = 5;
                break;
            case 3:
                offset = 2;
                break;
            default:
                offset = 2;
        }

        return offset;

  }

    drawMaleGametes() {
        var svdFont = this.ctx.font;

        var fontHeight = parseInt(this.ctx.font.match(/\d+/), 10);

        var gametes = this.punnettSquare.maleGametes();

        var fontSize = this.setGameteFontSize(gametes[0], this.colWidth, this.possibleGameteSizes());

        var x = this.padding.l + this.colWidth;
        for (var i = 0; i < gametes.length;++i) {
            this.setFontSize(fontSize, true);
            this.ctx.fillText(gametes[i], x, this.padding.t + this.rowHeight - this.textLift);
            this.setFontSize(fontSize - this.gameteFractionFontOffset(), false);
            this.ctx.fillText("1/" + gametes.length, x, this.padding.t + this.rowHeight - fontHeight - (this.textLift*(8 - this.punnettSquare.getNumTraits() * 2)));

            x = x + this.colWidth;
        }

        this.ctx.font = svdFont;


  }

  drawFemaleGametes() {
      var svdFont = this.ctx.font;

      var fontHeight = parseInt(this.ctx.font.match(/\d+/), 10);

      var gametes = this.punnettSquare.femaleGametes();

      var fontSize = this.setGameteFontSize(gametes[0], this.colWidth, this.possibleGameteSizes());

      var y = this.padding.t+ this.rowHeight * 2;
      for (var i = 0; i < gametes.length;++i) {
          this.setFontSize(fontSize, true);
          this.ctx.fillText(gametes[i], this.padding.l, y - this.textLift);
          this.setFontSize(fontSize - this.gameteFractionFontOffset(), false);
          this.ctx.fillText("1/" + gametes.length, this.padding.l, y - fontHeight - (this.textLift*(8 - this.punnettSquare.getNumTraits() * 2)));
          y = y + this.rowHeight;
      }

      this.ctx.font = svdFont;
  }

  drawGametes() {
      this.drawMaleGametes();
      this.drawFemaleGametes();
  }



  drawStuff(highlightOverride) {
      highlightOverride = highlightOverride || null; //supply this if want to highlighting certain phen or gen regardless of which punnett square hovered over. eg show all with certain ratio

      //this.drawLine(new Point(20,20), new Point(50,50));
      this.ctx.clearRect(0, 0, this.canvasEl.width, this.canvasEl.height);
      this.canvasEl.width+=0; //trick to refresh if above doesn't work
      if (this.state == PunnettSquareDiv.StateHidden) {}
      else {
          this.drawRowLines();
          this.drawColLines();
          this.drawGametes();
          this.drawTopCorner();
          this.drawCells();
          if (highlightOverride) {
              this.highlightCellsWithOverride(highlightOverride);
          }

      }

  }


}

PunnettSquareDiv.StateHidden = 1;
PunnettSquareDiv.StateMeiosis = 2;
PunnettSquareDiv.StateFertilised = 3;



class RatioTable {

    constructor(punnettSquare, ratioTableEl, staticPrefix, rowCallback, state) {
        this.punnettSquare = punnettSquare;
        this.ratioTableEl = ratioTableEl;
        this.staticPrefix = staticPrefix;
        this.state = state || PunnettSquareDiv.StateHidden;
        this.rowCallback = rowCallback;
        this.createRows();
    }

    imgUrlFromPhen(phen) {
      var phenImgURL = this.staticPrefix + "img/" + this.punnettSquare.genomeName + '/' +  this.punnettSquare.genomeName + '_' + phen + ".png";
      return phenImgURL
    }

    handleRowClick(e, row) {
        //alert('row clicked: ' + row.rowIndex);
        this.rowCallback(e, row);
    }

    addRow(cell1Text, cell2Text) {
        var row = this.ratioTableEl.insertRow(-1);
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        cell1.innerHTML = cell1Text;
        cell2.innerHTML = cell2Text;
        var svdThis = this;
        row.addEventListener('click', function(e) {
            svdThis.handleRowClick(e, row);
        });
    }

    createRows() {
        var numSquares = this.punnettSquare.numSquares();

        var numRows = this.ratioTableEl.rows.length;
        for (i = 0; i < numRows -1; ++i) {
           this.ratioTableEl.deleteRow(-1);
        }

        if (this.punnettSquare.genPhen == 'g') {
            var unique = this.punnettSquare.uniqueGenotypes();
            for (var i = 0; i < unique.length; ++i) {
                this.addRow(unique[i].gen, unique[i].count + " / " + numSquares);
            }
        }
        else {
            var unique = this.punnettSquare.uniquePhenotypes();
            for (var i = 0; i < unique.length; ++i) {
                var cellHTML = "<img src='" + this.imgUrlFromPhen(unique[i].phen) + "' alt='hello' width='60px'/>";
                this.addRow(cellHTML, unique[i].count + " / " + numSquares);
            }
        }

        var allRows = this.ratioTableEl.rows;
        // allRows[allRows.length-2].scrollIntoView({
        //     behavior: 'smooth',
        //     block: 'center'
        // });
        allRows[allRows.length-2].scrollIntoView();
    }

    setState(state) {
        this.state = state;
        if (this.state == PunnettSquareDiv.StateFertilised) {
            this.ratioTableEl.style.display = "block";
            var allRows = this.ratioTableEl.rows;
            // allRows[allRows.length-2].scrollIntoView({
            //     behavior: 'smooth',
            //     block: 'center'
            // });
           
        }
        else {
            this.ratioTableEl.style.display = "none";
        }
    }

}