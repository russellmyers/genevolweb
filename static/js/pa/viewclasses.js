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

class OrgCell {
    constructor(parent, org, pos, dim ) {
        this.parent = parent;
        this.org = org;
        this.pos = pos;
        this.dim = dim;
        this.ctx = this.parent.ctx;
        this.text = 'Aa';
    }

    get cellSize() {
        return this.dim;
    }

    get cellPosition() {
        return this.pos;
    }

    get actInhKey() {
        var actInhKey =  this.parent.parent.pedigree.actual;
        return actInhKey;

    }

    get showInhKey() {
        var showInhKey = this.parent.parent.inhTypeToShow;
        return showInhKey
    }

    get showGenTexts() {
        return this.parent.parent.showGenotypes;
    }

    // get cellPosition() {
    //     return new Point(this.parent.padding.l + this.cellSize.w * (this.c + 1), this.parent.padding.t + this.cellSize.h * (this.r + 1));
    // }

    drawGenotypeText(genotypeText) {
        this.ctx.font = "12px Arial";
        this.ctx.textBaseline = 'middle';
        this.ctx.fillStyle =  this.org.afflicted ? 'white' : 'black';

        if ((this.showInhKey == 'AR') || (this.showInhKey == 'AD') || (this.showInhKey == 'YR')){
            var w = this.ctx.measureText(genotypeText).width;
            //var hApprox = this.ctx.measureText('M').width;

            this.ctx.fillText(genotypeText,this.cellPosition.x + 1 + (this.cellSize.w / 2) - w/2, this.cellPosition.y + this.cellSize.h/2);

        }

        else if ((this.showInhKey == 'XR') || (this.showInhKey == 'XD')) {
            var textLen = 0;
            var offsets = [0];
            for (var i = 0; i < genotypeText.length; ++i) {
                var genCh = genotypeText.charAt(i);
                if ((genCh == 'X') || (genCh == '-') || (genCh == 'Y')) {
                    this.ctx.font = "12px Arial";
                    this.ctx.textBaseline = 'middle';
                } else {
                    this.ctx.font = "11px Arial";
                    this.ctx.textBaseline = 'alphabetic';
                }
                textLen += this.ctx.measureText(genCh).width;
                offsets.push(this.ctx.measureText(genCh).width);


            }

            var startX  = this.cellPosition.x + 1 + (this.cellSize.w / 2) - textLen/2;

            for (var i = 0; i < genotypeText.length; ++i) {
                var genCh = genotypeText.charAt(i);
                startX += offsets[i];
                if ((genCh == 'X') || (genCh == 'Y') || (genCh == '-')) {
                    this.ctx.font = "12px Arial";
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(genCh, startX, this.cellPosition.y + this.cellSize.h/2);

                } else {
                    this.ctx.font = "11px Arial";
                    this.ctx.textBaseline = 'alphabetic';
                    this.ctx.fillText(genCh, startX, this.cellPosition.y + this.cellSize.h/2);

                }

            }


        }
        // var w = this.ctx.measureText(txt).width;
        // //var hApprox = this.ctx.measureText('M').width;
        // //this.ctx.fillStyle =  this.org.afflicted ? 'white' : 'black';
        //
        // this.ctx.fillText(txt,this.cellPosition.x + 1 + (this.cellSize.w / 2) - w/2, this.cellPosition.y + this.cellSize.h/2 + hApprox/2);

    }

    draw(alpha) {

        alpha = alpha || 1.0;

        this.ctx.save();

        this.ctx.clearRect(this.cellPosition.x,this.cellPosition.y,this.cellSize.w,this.cellSize.h);
        this.ctx.strokeStyle = "black";
        this.ctx.lineWidth = 1;
        if (this.org.sex == 'male') {
            if (this.org.afflicted) {
                this.ctx.fillStyle = 'black';
            }
            else {
                this.ctx.fillStyle = 'white';
            }
            this.ctx.fillRect(this.cellPosition.x + 1, this.cellPosition.y + 1, this.cellSize.w - 2, this.cellSize.h - 2);

        }
        else {
            var r = this.cellSize.w / 2;

            this.ctx.beginPath();
            //this.parent.ctx.arc(100, 75, 50, 0, 2 * Math.PI);
            this.ctx.arc(this.cellPosition.x + 1 + r, this.cellPosition.y + 1 + r, r, 0, 2 * Math.PI);
            if (this.org.afflicted) {
                this.ctx.fillStyle = 'black';
            } else {
                this.ctx.fillStyle = 'white';
            }
            this.ctx.fill();
        }
        this.ctx.fillStyle = 'black';
        this.ctx.fillText(this.org.id,this.cellPosition.x + 1 + (this.cellSize.w / 2), this.cellPosition.y  + this.cellSize.h + 10);


        if (this.showInhKey  == null) {

        }
        else {

            var txt = this.org.inferrable_genotypes[this.showInhKey];
            var uninferrables = {'AR': 'A-', 'AD': '-a', 'XR': 'XAX-', 'XD': 'X-Xa', 'YR': 'X-Y'}
            txt = txt || uninferrables[this.showInhKey];
            // this.ctx.font = "12px Arial";
            // var w = this.ctx.measureText(txt).width;
            // var hApprox = this.ctx.measureText('M').width;
            // this.ctx.fillStyle =  this.org.afflicted ? 'white' : 'black';
            // this.ctx.fillText(txt,this.cellPosition.x + 1 + (this.cellSize.w / 2) - w/2, this.cellPosition.y + this.cellSize.h/2 + hApprox/2);
            if (this.showGenTexts) {
                this.drawGenotypeText(txt);
            }
        }

        this.ctx.restore();
    }


}


class OrgPairCell {
   constructor(parent, org, partner, pos, partnerPos, orgDim ) {
        this.parent = parent;
        this.org = org;
        this.partner = partner;
        this.pos = pos;
        this.partnerPos = partnerPos || null;
        this.orgDim = orgDim;
        if (this.partner == null) {
            this.pairWidth = this.orgDim.w;
        }
        else {
            this.pairWidth = this.orgDim.w * 2 + OrgPairCell.PartnerSpacing;
        }
        this.dim = this.orgDim || this.calcDim();
        this.ctx = this.parent.ctx;

        this._childOrgPairCells = [];

        this._orgCells = [];

        this.initOrgCells();



    }

    calcDim() {
       return new Dimension(this.pairWidth, this.orgDim.h)
    }

    initOrgCells() {
       this.addOrgCell(this.org, this.pos);
       if (this.partner == null) {
       }
       else        {
           if (this.partnerPos == null) {
               this.partnerPos = new Point(this.pos.x + this.parent.orgDim.w + OrgPairCell.PartnerSpacing, this.pos.y);
           }
           this.addOrgCell(this.partner, this.partnerPos);
       }


    }

    addOrgCell(org, pos) {
       var orgCell = new OrgCell(this, org, pos, this.orgDim);
       this._orgCells.push(orgCell);

    }

    draw() {
       for (var i = 0; i < this._orgCells.length; ++i) {
           var orgCell = this._orgCells[i];
           orgCell.draw();
       }
       this.drawPartnerLink();

       this.drawChildrenLinks();

      // if (this.partner == null) {
      //     this.pairWidth = this.parent.orgDim.w;
      // }
      //
      // this.org.draw();
      // if (this.partner == null) {
      //
      // }
      // else {
      //     this.partner.draw();
      //     this.drawLink();
      // }


    }

    drawPartnerLink() {
       if (this._orgCells.length < 2) {
           return;
       }
        this.ctx.beginPath();
        this.ctx.moveTo(this._orgCells[0].pos.x + this._orgCells[0].dim.w, this._orgCells[0].pos.y + (this._orgCells[0].dim.h /2));
        this.ctx.lineTo(this._orgCells[1].pos.x, this._orgCells[1].pos.y +(this._orgCells[1].dim.h /2 ));
        this.ctx.stroke();
    }

    addChildOrgPairCell(orgPairCell) {
       this._childOrgPairCells.push(orgPairCell);
    }

    drawChildrenLinks() {

       if (this._childOrgPairCells.length == 0) {
           return;//
       }

       // First drop
       this.ctx.beginPath();
       this.ctx.moveTo(this.pos.x + (this.pairWidth/2), this.pos.y+ (this.orgDim.h / 2));
       this.ctx.lineTo(this.pos.x + (this.pairWidth/2), this.pos.y + PedigreeDiagram.LevelHeight * 2 / 3);
       this.ctx.stroke();

       // Span
       var firstChildOrgPairCell =  this._childOrgPairCells[0];
       var lastChildOrgPairCell =  this._childOrgPairCells[this._childOrgPairCells.length-1];
       var startX = firstChildOrgPairCell.pos.x +  (this.orgDim.w/2); //(firstChildOrgPairCell.pairWidth/2);
       var endX = (this._childOrgPairCells.length == 1) ?  this.pos.x + (this.pairWidth/2) : lastChildOrgPairCell.pos.x + (this.orgDim.w/2); // (lastChildOrgPairCell.pairWidth/2);
       var spanY = this.pos.y + PedigreeDiagram.LevelHeight  * 2 / 3;
       this.ctx.moveTo(startX, spanY);
       this.ctx.lineTo(endX, spanY);
       this.ctx.stroke();

        // Second drop
       for (var i = 0;i < this._childOrgPairCells.length;++i) {
           var childOrgPairCell = this._childOrgPairCells[i];
           this.ctx.beginPath();
           // if ((i == 0)  && (this._childOrgPairCells.length == 1)) {
           //     this.ctx.moveTo(this.pos.x + (this.pairWidth/2), spanY);
           //     this.ctx.lineTo(this.pos.x + (this.pairWidth/2), this.pos.y + PedigreeDiagram.LevelHeight);
           // }
           // else {
           this.ctx.moveTo(childOrgPairCell.pos.x + (this.orgDim.w / 2), spanY);
           this.ctx.lineTo(childOrgPairCell.pos.x + (this.orgDim.w / 2), this.pos.y + PedigreeDiagram.LevelHeight);
           //}
           this.ctx.stroke();
       }

    }

}

OrgPairCell.PartnerSpacing = 10


class PedigreeDiagram {

  constructor(pedigree, canvasEl, staticPrefix, padding) {
    this.pedigree = pedigree;
    this.canvasEl = canvasEl;
    this.ctx = this.canvasEl.getContext('2d');
    this.padding = padding ||  {'t':10, 'b': 10, 'l': 10, 'r': 10}
    this.staticPrefix = staticPrefix;
    this.orgDim = new Dimension(30,30);
    this.showGenotypes = false;
    this.inhTypeToShow = null;

    this._orgPairCells = [];

    var self = this;

    this.initOrgPairCells();

    // this.canvasEl.onmousemove =  function(e) {
    // };

  //   this.punnettCells = this.createPunnettCells();
  //
  }


  createOrgCells() {

      // var punnettCells = [];
      //
      // for (var r = 0; r < this.numRows -1; ++r) {
      //     for (var c =0; c < this.numCols -1; ++c) {
      //         punnettCells.push(new PunnettCell(this, r, c));
      //     }
      // }
      //
      // return punnettCells;
  }



  get canvasSize() {
      const { width, height } = this.canvasEl.getBoundingClientRect();
      return {'w': width, 'h': height}
  }

  get usableHeight() {
      var size = this.canvasSize;
      var height =  (size.h - this.padding.t - this.padding.b);
      return height;
  }

  get usableWidth() {
      var size = this.canvasSize;
      var width =  (size.w - this.padding.l - this.padding.r);
      return width;
  }

  initOrgPair(orgPair, availSpace) {

      // Create OrgPairCell for orgpair

      var orgPairCell = this.addOrgPairCell(orgPair, null, null, availSpace);

      // recursive initOrgPair() for every child

     var childPairs = this.pedigree.getChildOrgPairs(orgPair);

     var tot_grandchildren = 0
     for (var i = 0;i < childPairs.length;++i) {
         var childPair = childPairs[i];
         tot_grandchildren += childPair[0].children.length;
         tot_grandchildren += 1; // add 1 for each child to ensure at least 1 space if no grandchildren
     }
     var unitSpace = (availSpace[1] -availSpace[0]) / tot_grandchildren;
     var prevAvailSpaceEnd = availSpace[0];

     for (var i = 0;i < childPairs.length;++i) {
         var childPair = childPairs[i];
         var availSpaceStart =  prevAvailSpaceEnd;
         var availSpaceEnd = availSpaceStart + unitSpace * (childPair[0].children.length + 1);
         var childAvailSpace = [availSpaceStart, availSpaceEnd];
         var childOrgPairCell = this.initOrgPair(childPair, childAvailSpace);  // addOrgPairCell(childPairs[i], null, null, availSpace);
         orgPairCell.addChildOrgPairCell(childOrgPairCell);
         prevAvailSpaceEnd = availSpaceEnd;
     }

      return orgPairCell;

      // Join orgpaircell to child orgpaircells




  }

  initOrgPairCells() {
      var hardCodedPoints = [new Point(250, 40), new Point(100, 100), new Point(200, 100), new Point(300, 100), new Point(400, 100)]
      var pairs = this.pedigree.orgPairs;

      var rootPair = pairs[0];
      var rootAvailXStart = 0;
      var rootAvailXEnd = this.usableWidth;
      var availSpace = [rootAvailXStart,rootAvailXEnd];
      this.initOrgPair(rootPair, availSpace);
      // this.addOrgPairCell(rootPair, null, null, availSpace);
      // var childPairs = this.pedigree.getChildOrgPairs(rootPair);
      // for (var i = 0;i < childPairs.length;++i) {
      //    var availSpaceStart =  rootAvailXStart + ((rootAvailXEnd - rootAvailXStart) / childPairs.length) * i;
      //    var availSpaceEnd = availSpaceStart + (((rootAvailXEnd - rootAvailXStart) / childPairs.length)) * (i+1);
      //    availSpace = [availSpaceStart, availSpaceEnd];
      //    this.addOrgPairCell(childPairs[i], null, null, availSpace);
      // }



  }

  joinOrgPairs(op1Org, op1Partner, op2Org, op2Partner) {


  }

  // linkOrgPair(c, partner) {
  //   this.ctx.beginPath();
  //   this.ctx.moveTo(c.pos.x + c.dim.w, c.pos.y + (c.dim.h /2));
  //   this.ctx.lineTo(partner.pos.x, partner.pos.y +(partner.dim.h /2 ));
  //   this.ctx.stroke();
  // }
  //
  // drawOrgPair(c, partner) {
  //     var pairWidth = this.orgDim.w * 2 + this.partnerSpacing;
  //     if (partner == null) {
  //         pairWidth = this.orgDim.w;
  //     }
  //
  //     c.draw();
  //     if (partner == null) {
  //
  //     }
  //     else {
  //         partner.draw();
  //         this.linkOrgPair(c, partner);
  //     }
  //
  //
  // }

  addOrgPairCell(orgPair, pos = null, yPos = null, availSpace = null) {
          // var c = new OrgCell(this, this.pedigree.orgWithId(pair[0]), hardCodedPoints[i], this.orgDim);
          // var partner = null
          // if (pair[1] == null) {
          //
          // } else {
          //     partner = new OrgCell(this, this.pedigree.orgWithId(pair[1]), null, this.orgDim);
          // }
         var usePos = pos;
         if (pos == null) {
             var level = orgPair[0].level;
             if (availSpace == null) {
                 availSpace = [0, this.usableWidth / level];

             }
             if (yPos == null) {
                 yPos = (level -1) * PedigreeDiagram.LevelHeight + this.padding.t;
             }
             var posX = availSpace[0] + ((availSpace[1] - availSpace[0]) / 2);
             if (orgPair[1]  == null) {
                posX = posX - (this.orgDim.w / 2);
             }
             else {
                 posX = posX - (this.orgDim.w + OrgPairCell.PartnerSpacing / 2);
             }

             var posY = yPos;
             usePos = new Point(posX, posY);

         }
          var orgPairCell = new OrgPairCell(this, orgPair[0], orgPair[1], usePos, null, this.orgDim);
          this._orgPairCells.push(orgPairCell);

          return orgPairCell
//
  }

  drawOrgPairs() {
      for (var i = 0; i < this._orgPairCells.length;++i) {
          var orgPairCell = this._orgPairCells[i];
          orgPairCell.draw();
      }
      // var pairWidth = this.orgDim.w * 2 + this.partnerSpacing;

      // var hardCodedPoints = [new Point(250, 40), new Point(100, 100), new Point(200, 100), new Point(300, 100), new Point(400, 100)]
      // var pairs = this.pedigree.orgPairs;
      // for (var i = 0;i < pairs.length;++i) {
      //     var pair = pairs[i];
      //     //var c = new OrgCell(this, this.pedigree.orgs[0], new Point(this.padding.l +  (this.usableWidth /2), this.padding.t), this.orgDim );
      //     var c = new OrgCell(this, this.pedigree.orgWithId(pair[0]), hardCodedPoints[i], this.orgDim);
      //     var partner = null
      //     if (pair[1] == null) {
      //
      //     } else {
      //         partner = new OrgCell(this, this.pedigree.orgWithId(pair[1]), null, this.orgDim);
      //     }
      //     var orgPair = new OrgPairCell(this, c, partner, c.pos, null)
      //     orgPair.draw()
      // }




      // var c = new OrgCell(this, this.pedigree.orgs[0], new Point(this.padding.l +  (this.usableWidth /2), this.padding.t), this.orgDim );
      //
      // var partner = new OrgCell(this,  this.pedigree.orgs[1], null, this.orgDim );
      //
      // var orgPair = new OrgPair(this, c, partner, c.pos, null )
      // orgPair.draw()


      // var c = new OrgCell(this, this.pedigree.orgs[2], new Point(this.padding.l + 100 , this.padding.t + 50), this.orgDim );
      // var orgPair = new OrgPair(this, c, null, c.pos, null )
      // orgPair.draw()





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

  resizeOrgPairCell(orgPairCell, availSpace) {
         var posX = availSpace[0] + ((availSpace[1] - availSpace[0]) / 2);
         if (orgPairCell._orgCells.length == 1) {
            posX = posX - (this.orgDim.w / 2);
         }
         else {
             posX = posX - (this.orgDim.w + OrgPairCell.PartnerSpacing / 2);
         }
         orgPairCell._orgCells[0].pos.x = posX;
         if (orgPairCell._orgCells.length == 1) {

         }
         else {
             orgPairCell._orgCells[1].pos.x = orgPairCell._orgCells[0].pos.x + this.orgDim.w + OrgPairCell.PartnerSpacing;
         }


     var childOrgPairCells = orgPairCell._childOrgPairCells;

     var tot_grandchildren = 0
     for (var i = 0;i < childOrgPairCells.length;++i) {
         var childOrgPairCell = childOrgPairCells[i];
         tot_grandchildren += childOrgPairCell._childOrgPairCells.length;
         tot_grandchildren += 1; // add 1 for each child to ensure at least 1 space if no grandchildren
     }
     var unitSpace = (availSpace[1] -availSpace[0]) / tot_grandchildren;
     var prevAvailSpaceEnd = availSpace[0];

     for (var i = 0;i < childOrgPairCells.length;++i) {
         var childOrgPairCell = childOrgPairCells[i];
         var availSpaceStart =  prevAvailSpaceEnd;
         var availSpaceEnd = availSpaceStart + unitSpace * (childOrgPairCell._childOrgPairCells.length + 1);
         var childAvailSpace = [availSpaceStart, availSpaceEnd];
         this.resizeOrgPairCell(childOrgPairCell, childAvailSpace);  // addOrgPairCell(childPairs[i], null, null, availSpace);
         prevAvailSpaceEnd = availSpaceEnd;
     }

  }

  resizeOrgPairCells() {
      var rootOrgPairCell = this._orgPairCells[0];
      var rootAvailXStart = 0;
      var rootAvailXEnd = this.usableWidth;
      var availSpace = [rootAvailXStart,rootAvailXEnd];
      this.resizeOrgPairCell(rootOrgPairCell,availSpace);

  }

  drawStuff(resize = false) {

      this.ctx.clearRect(0, 0, this.canvasEl.width, this.canvasEl.height);
      this.canvasEl.width+=0; //trick to refresh if above doesn't work

      // this.ctx.beginPath();
      // this.ctx.rect(this.padding.l, this.padding.t, this.usableWidth, this.usableHeight);
      // this.ctx.stroke();
      if (resize) {
          this.resizeOrgPairCells();
      }

      this.drawOrgPairs();

  }


}

PedigreeDiagram.LevelHeight = 80;
