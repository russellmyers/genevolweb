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

class Box {
    constructor(pos, dim) {
        this._pos = pos;
        this._dim = dim;
    }

    get w() {
        return this._dim.w;
    }

    get h() {
        return this._dim.h;
    }

    get x() {
        return this._pos.x;
    }

    get y() {
        return this._pos.y;
    }
}

class Cell {
   constructor(parent, pos, dim ) {
        this.parent = parent;
        this.pos = pos;
        this.dim = new Dimension(dim.w, dim.h);
        this.ctx = this.parent.ctx;
        this.text = '*';
        this.textFillStyle = 'black';
    }

    get cellSize() {
        return this.dim;
    }
    set cellSize(newSize) {
       this.dim = new Dimension(newSize.w, newSize.h);
    }

    get cellPosition() {
        return this.pos;
    }

    superSize() {
       this.dim.w += 4;
       this.dim.h += 4;
    }

    shrink() {
       this.dim.w -= 4;
       this.dim.h -= 4;
    }

    pointInCell(p) {
      if ((this.pos.x <= p.x) && (p.x <= (this.pos.x + this.dim.w)) && (this.pos.y <= p.y) && (p.y <= (this.pos.y + this.dim.h))) {
          return true;
      }
      else {
         return false;
      }
    }

    /**
     * Redefine in subclasses
     * @param alpha - transparency
     * @private
     */
    _draw(alpha) {
        this.ctx.font = "14px Arial";
        this.ctx.fillStyle =  this.textFillStyle; //'black';
        this.ctx.fillText(this.text, this.cellPosition.x , this.cellPosition.y+10);
    }


    draw(alpha, dontClear) {

        dontClear = dontClear || false;

        alpha = alpha || 1.0;

        this.ctx.save();

        if (dontClear) {
        }
        else {
            this.ctx.clearRect(this.cellPosition.x, this.cellPosition.y, this.cellSize.w, this.cellSize.h);
        }

        this._draw(alpha);

        this.ctx.restore();

    }


}


/**
 * Attributes:
 *
 * this.proposedText = genotype proposed by user
 */
class OrgCell extends Cell {

    constructor(parent, org, pos, dim ) {
        super(parent, pos, dim);
        this.org = org;
        this.text = 'Aa';
        this.proposedTexts = {};
        for (var key in this.org.inferrable_genotypes) {
            if (this.org.inferrable_genotypes.hasOwnProperty(key)) {
                this.proposedTexts[key] = null;
            }
        }
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

    drawTick() {

        var correct = this.correctGuess();
        var img = correct ? this.parent.parent.tickImg : this.parent.parent.crossImg;
        if (img ==  null) {
            return;
        }

        var xPos =  null;
        if (this.org.isInLaw) {
            xPos = this.cellPosition.x; //this.cellPosition.x + this.cellSize.w + 5;
        }
        else {
            xPos = this.cellPosition.x; //this.cellPosition.x - 15 - 5;
        }
        this.ctx.drawImage(img, xPos, this.cellPosition.y + this.cellSize.h, 12, 12);

    }

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

    getInferrableGenotypeText() {
            var txt = this.org.inferrable_genotypes[this.showInhKey];
            var uninferrables = {'AR': 'A-', 'AD': '-a', 'XR': 'XAX-', 'XD': 'X-Xa', 'YR': 'X-Y'}
            txt = txt || uninferrables[this.showInhKey];
            return txt;


    }

    getProposedGenotypeText() {
           return this.proposedTexts[this.showInhKey];
    }

    correctGuess(exclUninferrables=false) {
        if (exclUninferrables ) {
           if (this.org.inferrable_genotypes[this.showInhKey] == null) {
               return false;
           }

        }

        return this.getInferrableGenotypeText() == this.getProposedGenotypeText();
    }

    _draw(alpha) {

        //alpha = alpha || 1.0;

        //this.ctx.save();

        //this.ctx.clearRect(this.cellPosition.x,this.cellPosition.y,this.cellSize.w,this.cellSize.h);
        this.ctx.strokeStyle = "black";
        this.ctx.lineWidth = 1;
        if (this.org.sex == 'male') {
            if (this.org.afflicted) {
                this.ctx.fillStyle = 'black';
            }
            else {
                this.ctx.fillStyle = 'white';
            }
            this.ctx.strokeRect(this.cellPosition.x, this.cellPosition.y, this.cellSize.w, this.cellSize.h);
              this.ctx.fillRect(this.cellPosition.x + 1, this.cellPosition.y + 1, this.cellSize.w - 2, this.cellSize.h - 2);
            this.ctx.lineWidth = 1;
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
            this.ctx.lineWidth = 1;
            this.ctx.strokeStyle = '#000000';
            this.ctx.stroke();
            this.ctx.closePath();
        }
        this.ctx.fillStyle = 'black';
        this.ctx.fillText(this.org.id,this.cellPosition.x + 1 + (this.cellSize.w / 2) - 5, this.cellPosition.y  + this.cellSize.h + 10);


        if (this.showInhKey  == null) {

        }
        else {
            var txt = this.getInferrableGenotypeText();
            var proposedTxt = this.getProposedGenotypeText();
            // this.ctx.font = "12px Arial";
            // var w = this.ctx.measureText(txt).width;
            // var hApprox = this.ctx.measureText('M').width;
            // this.ctx.fillStyle =  this.org.afflicted ? 'white' : 'black';
            // this.ctx.fillText(txt,this.cellPosition.x + 1 + (this.cellSize.w / 2) - w/2, this.cellPosition.y + this.cellSize.h/2 + hApprox/2);
            var txtColour = this.org.afflicted ? 'white' : 'black';
            if (this.showGenTexts) {
                //this.drawGenotypeText(txt);
                pd.drawGenotypeText(this.ctx, txt, new Box(this.cellPosition, this.cellSize), this.showInhKey, txtColour);
            }
            else if (!(proposedTxt == null)) {
                //this.drawGenotypeText(proposedTxt);
                pd.drawGenotypeText(this.ctx, proposedTxt, new Box(this.cellPosition, this.cellSize), this.showInhKey, txtColour);
                this.drawTick();
            }
        }

        //this.ctx.restore();
    }


}

OrgCell.defaultSize = {'w':30,'h':30};
OrgCell.defaultOverSize = {'w':32, 'h': 32};

class OrgPairCell extends Cell {
   constructor(parent, org, partner, pos, partnerPos, orgDim ) {
        super(parent, pos, orgDim);
        //this.parent = parent;
        this.org = org;
        this.partner = partner;
        //this.pos = pos;
        this.partnerPos = partnerPos || null;
        this.orgDim = orgDim;
        if (this.partner == null) {
            this.pairWidth = this.orgDim.w;
        }
        else {
            this.pairWidth = this.orgDim.w * 2 + OrgPairCell.PartnerSpacing;
        }
        this.dim = this.orgDim || this.calcDim();
        //this.ctx = this.parent.ctx;

        this._childOrgPairCells = [];

        this._orgCells = [];

        this.initOrgCells();

        this._draggingCell = null;


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

    addDraggingCell(pos, text) {
       this._draggingCell = new Cell(this, pos, {'w':50,'h':20})
       this._draggingCell.text = text;
    }

    removeDraggingCell() {
       this._draggingCell = null;
    }

    _draw(alpha) {
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

/**
 * Genotype selection cell
 */
class GenCell extends Cell {
    constructor(parent, pos, dim, isSelected=false ) {
        super(parent, pos, dim);
        this.text = 'XAXa';
        this.backgroundFillStyle = 'beige';
        this.isSelected = isSelected;
    }


    _draw(alpha) {
    this.ctx.font = "18px Helvetica Neue";

     var w = null;
     var h = null;
     if (true) {
         //auto-size
         w = this.ctx.measureText(this.text).width + 5;
         h = this.ctx.measureText('M').width + 5;
     }
     else {
         w = this.dim.w;
         h = this.dim.h;
     }

     if (this.isSelected) {
         this.backgroundFillStyle = '#00A000';
     }
     else {
          this.backgroundFillStyle = 'beige';
     }
     this.ctx.strokeStyle = 'black';
     this.ctx.strokeRect(this.pos.x, this.pos.y, w, h);
     this.ctx.fillStyle = this.backgroundFillStyle;
     this.ctx.fillRect(this.pos.x+1,this.pos.y+1,w - 2,h-2);
     this.ctx.fillStyle = 'black';
     pd.drawGenotypeText(this.ctx, this.text, new Box(this.pos, new Dimension(w, h)), pd.inhTypeToShow, 'black', 14);
     //this.ctx.fillText(this.text, (this.pos.x + 2), (this.pos.y + h - 5));

    }

    /** Override parent methods: - set background light instead of making bigger
     *
     */
    superSize() {
       this.backgroundFillStyle = '#00A000';
    }

    shrink() {
       this.backgroundFillStyle = 'beige';

    }


}



/** Class representing a pedigree diagram drawn within a canvas element.
 *  Paired with a Pedigree model object which contains the pedigree details
 *
 *   Object attributes:
 *  - pedigree - pedigree object
 *  - canvasEl - canvas element to draw pedigree diagram in
 *  - staticPrefix - prefix to static file location
 *  - padding - padding around pedigree diagram (dict - 't', 'b', 'l', 'r')
 *  - orgDim: Size of orgs
 *  - showGenotypes: flag indicating whether to show genotypes
 *  - inhTypeToShow: inheritance type to show
 *  - _orgPairCells: List of OrgPairCell cells (ie org and partner cells)
 *
 *  Object properties:
 *  - canvasSize
 *  - useableHeight (canvas height - top and bottom padding)
 *  - useableWidth (canvas widht - left and right padding)
 */
class PedigreeDiagram {

    /**
     *
     * @param pedigree - pedigree object associated with diagram
     * @param canvasEl - canvas element to draw pedigree diagram in
     * @param staticPrefix - prefix to static file location
     * @param padding - padding around pedigree diagram (dict - 't', 'b', 'l', 'r')
     *
     */
  constructor(pedigree, canvasEl, staticPrefix, padding) {
    this.pedigree = pedigree;
    this.canvasEl = canvasEl;
    this.ctx = this.canvasEl.getContext('2d');
    this.padding = padding ||  {'t':10, 'b': 10, 'l': 10, 'r': 10}
    this.staticPrefix = staticPrefix;
    this.orgDim = new Dimension(30,30);
    this.showGenotypes = false;
    this.inhTypeToShow = null;
    this.tickImg = null;
    this.crossImg = null;

    this._orgPairCells = [];

    var self = this;

    this.initOrgPairCells();

    this.createGenCells(['XAXA','XAXa', 'XaXa', 'XAX-', 'XQXq']);

    this.loadImages();
    // this.canvasEl.onmousemove =  function(e) {
    // };

  //   this.punnettCells = this.createPunnettCells();
  //
  }


  loadImages() {
      var imgTick = new Image();
      var self = this;
      imgTick.onload = function() {
          // image loaded
          self.tickImg = imgTick;
      }
      imgTick.src = this.staticPrefix + 'img/tick.png';
      var imgCross = new Image();
      imgCross.onload = function() {
          // image loaded
          self.crossImg = imgCross;
      }
      imgCross.src = this.staticPrefix + 'img/cross.PNG';

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

  createGenCells(genTexts=[]) {
      this.gCells = [];
      var xPos = 100;
      var yPos = 350;
      //var genTexts = ['XAXA','XAXa', 'XaXa', 'XAX-'];
      for (var i=0;i < genTexts.length;++i) {
          var isSelected = (i == 0) ? true : false;

          var gCell = new GenCell(this, {'x': xPos, 'y': yPos},{'w': 50, 'h': 20}, isSelected = isSelected);
          gCell.text = genTexts[i];
          this.gCells.push(gCell);
          xPos += 60;
      }

  }

  selectGenCell(gCell) {
      for (var i = 0;i < this.gCells.length;++i) {
          if (this.gCells[i] == gCell) {
              this.gCells[i].isSelected = true;
          }
          else {
              this.gCells[i].isSelected = false;
          }
      }
  }

  get selectedGenCell() {
      for (var i = 0;i < this.gCells.length;++i) {
          if (this.gCells[i].isSelected) {
              return this.gCells[i];

          }
      }
      return null;
  }

  addDraggingCell(pos, text) {
      this._draggingCell = new Cell(this, pos, {'w': 50, 'h': 20});
      this._draggingCell.text = text;
  }

  removeDraggingCell() {
      this._draggingCell = null;
  }

  pointInGenCells(p) {

      for (var i=0;i < this.gCells.length;++i) {
          var gCell = this.gCells[i];
          if (gCell.pointInCell(p)) {
              return gCell;
          }
      }

      return null;
  }

  pointInOrgCells(p) {
     for (var i=0;i < this._orgPairCells.length;++i) {
          var orgPairCell = this._orgPairCells[i];
          for (var j= 0;j < orgPairCell._orgCells.length; ++j) {
              var orgCell = orgPairCell._orgCells[j];
              if (orgCell.pointInCell(p)) {
                  return orgCell;
              }
          }
     }

      return null;

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

    /**
     * Recursive method to initialise an OrgPairCell for on orgPair and all its child orgPairs.
     *
     * Available space calculation:
     * - add OrgPairCell for current orgPair using availSpace
     * - For each child of current OrgPair:  determine proportion  of available space depending on how many children **that** child has, and call ths method recursively to create OrgPairCell for each child and link each child OrgPairCell as child of OrgPairCell for current orgPair
     * @param orgPair - org pair to initialise
     * @param availSpace - available space to create orgPairCell in
     * @returns {OrgPairCell} - created OrgPairCell
     */
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

    /**
     * Get root org pair from pedigree and call initOrgPair for root pair (which then recursively inits all other org pairs)
     */
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


    /**
     * Create OrgPairCell  for an orgPair and add to this._orgPairCells list
     * @param orgPair
     * @param pos - optional: if not specified, automatically determine x pos depending on avail space
     * @param yPos - optional: if not specified, automatically determine y pos
     * @param availSpace
     * @returns {OrgPairCell}
     */

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

  drawGenotypeText(ctx, genotypeText, box, inhType='AR',  textFontColour='black', textFontSize=12) {
      /**
       * Utility to draw specified genotypeText centered in specified box, with superscripts etc
       *
       */
        ctx.save();

        ctx.font = textFontSize + "px Arial";
        ctx.textBaseline = 'middle';
        ctx.fillStyle =  textFontColour;

        if ((inhType == 'AR') || (inhType == 'AD') || (inhType == 'YR')){
            var w = ctx.measureText(genotypeText).width;
            //var hApprox = this.ctx.measureText('M').width;

            ctx.fillText(genotypeText,box.x + 1 + (box.w / 2) - w/2, box.y + box.h/2);

        }

        else if ((inhType == 'XR') || (inhType == 'XD')) {
            var textLen = 0;
            var offsets = [0];
            for (var i = 0; i < genotypeText.length; ++i) {
                var genCh = genotypeText.charAt(i);
                if ((genCh == 'X') || (genCh == '-') || (genCh == 'Y')) {
                    ctx.font =  textFontSize + "px Arial";
                    ctx.textBaseline = 'middle';
                } else {
                    ctx.font = textFontSize - 1 + "px Arial";
                    ctx.textBaseline = 'alphabetic';
                }
                textLen += ctx.measureText(genCh).width;
                offsets.push(ctx.measureText(genCh).width);


            }

            var startX  = box.x + 1 + (box.w / 2) - textLen/2;

            for (var i = 0; i < genotypeText.length; ++i) {
                var genCh = genotypeText.charAt(i);
                startX += offsets[i];
                if ((genCh == 'X') || (genCh == 'Y') || (genCh == '-')) {
                    ctx.font = textFontSize + "px Arial";
                    ctx.textBaseline = 'middle';
                    ctx.fillText(genCh, startX, box.y + box.h/2);

                } else {
                    ctx.font = textFontSize - 1 + "px Arial";
                    ctx.textBaseline = 'alphabetic';
                    ctx.fillText(genCh, startX, box.y + box.h/2);

                }

            }


        }

        ctx.restore();
        // var w = this.ctx.measureText(txt).width;
        // //var hApprox = this.ctx.measureText('M').width;
        // //this.ctx.fillStyle =  this.org.afflicted ? 'white' : 'black';
        //
        // this.ctx.fillText(txt,this.cellPosition.x + 1 + (this.cellSize.w / 2) - w/2, this.cellPosition.y + this.cellSize.h/2 + hApprox/2);

    }


  drawAlleleLegend() {
     this.ctx.save();
     if (this.showGenotypes) {
         //this.inhTypeToShow = null;
         var txt = 'Wild type Allele - A, Afflicted Allele - a'
         if (this.inhTypeToShow == 'YR') {
             txt = 'Wild type Allele - Y, Afflicted Allele - y'
         }

         this.ctx.font = "14px Helvetica Neue"; //Arial";
         var textWidth = this.ctx.measureText(txt).width;
         this.ctx.fillText(txt, this.padding.l + this.usableWidth - textWidth - 10, this.padding.t + 10);
     }
     this.ctx.restore()


  }

  drawPhenotypeLegend() {
     this.ctx.save();

     //this.ctx.scale(0.2, 0.2)

     //this.ctx.fillText("Hello there", canvas.width / 2 * 1 / 0.3, canvas.height * 2.8 / 4 * 1 / 0.3, canvas.width * 0.9 * 1 / 0.3);
    //this.ctx.font = canvas.width / 15 + "px Arial";
    //this.ctx.fillText("Want to talk? Mail me at mher@movsisyan.info", canvas.width / 2 * 1 / 0.3, canvas.height * 3.6 / 4 * 1 / 0.3, canvas.width * 0.9 * 1 / 0.3);
    //this.ctx.fillText("Want to see my code? Find me on GitHub as MovsisyanM", canvas.width / 2 * 1 / 0.3, canvas.height * 3.8 / 4 * 1 / 0.3, canvas.width * 0.9 * 1 / 0.3);


     // this.ctx.font = "60px Helvetica Neue"; //Arial";
     // this.ctx.fillText('Afflicted individual',10*5 ,20*5);
     // this.ctx.font = "150px Helvetica Neue"; //Arial";
     // this.ctx.fillText('\u{25A0}',110*5,20*5);
     // this.ctx.font = "60px Helvetica Neue"; //Arial";
     // this.ctx.fillText('Unafflicted individual',150*5,20*5);
     // this.ctx.font = "150px Helvetica Neue"; //Arial";
     // this.ctx.fillText('\u{25A1}',260*5,20*5);

     this.ctx.font = "12px Helvetica Neue"; //Arial";
     this.ctx.fillText('Afflicted individual',10 ,20);
     this.ctx.font = "30px Helvetica Neue"; //Arial";
     this.ctx.fillText('\u{25A0}',110,20);
     this.ctx.font = "12px Helvetica Neue"; //Arial";
     this.ctx.fillText('Unafflicted individual',150,20);
     this.ctx.font = "30px Helvetica Neue"; //Arial";
     this.ctx.fillText('\u{25A1}',260,20);


     this.ctx.font = "12px Helvetica Neue"; //Arial";
     this.ctx.fillText('Male ',10,45);
     this.ctx.font = "30px Helvetica Neue"; //Arial";
     this.ctx.fillText('\u{25A1}',40,45);
     this.ctx.font = "12px Helvetica Neue"; //Arial";
     this.ctx.fillText('Female ',75,45);
     this.ctx.font = "30px Helvetica Neue"; //Arial";
     this.ctx.fillText('\u{25CB}',115,48);

     //this.ctx.scale(1, 1)

     // var txt = 'Wild type Allele - A, Afflicted Allele - a'
     // if (this.inhTypeToShow == 'YR') {
     //     txt = 'Wild type Allele - Y, Afflicted Allele - y'
     // }
     //
     // this.ctx.font = "14px Helvetica Neue"; //Arial";
     // var textWidth = this.ctx.measureText(txt).width;
     // this.ctx.fillText(txt, this.padding.l + this.usableWidth - textWidth - 10, this.padding.t + 10);

     this.ctx.restore()


  }


    /**
     * Master draw method for PedigreeDiagram
     * Calls:
     * - drawAlleleLegend()
     * - drawPhenotypeLegend()
     * - drawOrgPairs()
     *
     * @param resize - if specified, automatically resize all org pair cells before drawing
     */
  drawStuff(resize = false) {

      this.ctx.clearRect(0, 0, this.canvasEl.width, this.canvasEl.height);
      this.canvasEl.width+=0; //trick to refresh if above doesn't work


      // this.ctx.beginPath();
      // this.ctx.rect(this.padding.l, this.padding.t, this.usableWidth, this.usableHeight);
      // this.ctx.stroke();
      if (resize) {
          this.resizeOrgPairCells();
      }


      this.drawAlleleLegend();

      this.drawPhenotypeLegend();

      this.drawOrgPairs();

      if (this.inhTypeToShow == null) {

      }
      else {
          for (var i = 0; i < this.gCells.length; ++i) {
              this.gCells[i].draw();
          }
          if (this.gCells.length > 0) {
              this.ctx.font = "16px Helvetica Neue"; //Arial";
              this.ctx.fillText('Genotype toolbox', this.gCells[0].pos.x, this.gCells[0].pos.y - 10);
              this.ctx.font = "14px Helvetica Neue"; //Arial";
              this.ctx.fillText('(Select genotype from toolbox and click on organisms to infer genotypes)', this.gCells[0].pos.x, this.gCells[0].pos.y + 40);
          }
      }

      if (this._draggingCell == null) {

      }
      else {
          this._draggingCell.draw(null, true);
      }


  }


}

PedigreeDiagram.LevelHeight = 80;

