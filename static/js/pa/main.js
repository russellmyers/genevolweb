// Main code


function fitToContainer(canvas){
  // Make it visually fill the positioned parent
  canvas.style.width ='100%';
  canvas.style.height='100%';
  // ...then set the internal size to match
  canvas.width  = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}

function numConsistent() {
    var numCons = 0
    for (key in consistentPerInferrer) {
        if (consistentPerInferrer[key] == 0) {

        }
        else {
            numCons +=1;
        }
    }
    return numCons;

}




canvasEl = document.getElementById('canvas');
var pedigreeJson = {
    'orgs':[
        {'id':1, 'sex':'male', 'afflicted':false, 'children':[3, 4, 5, 6], 'partner':2, 'level': 1, 'isInlaw':false},
        {'id':2, 'sex': 'female', 'afflicted':true, 'children':[], 'partner': null, 'level': 1, 'isInlaw':false},
        {'id':3, 'sex': 'female', 'afflicted':false, 'children':[8,9], 'partner': 7, 'level':2, 'isInlaw':false},
        {'id':4, 'sex': 'male', 'afflicted':false, 'children':[12], 'partner': 11, 'level':2, 'isInlaw':false},
        {'id':5, 'sex': 'female', 'afflicted':false, 'children':[17], 'partner': 16, 'level':2, 'isInlaw':false},
        {'id':6, 'sex': 'male', 'afflicted':false, 'children':[24, 25, 26, 27], 'partner': 23, 'level':2, 'isInlaw':true},
        {'id':7, 'sex': 'female', 'afflicted':true, 'children':[], 'partner': null, 'level':2, 'isInlaw':false},
        {'id':8, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': 10, 'level':3, 'isInlaw':false},
        {'id':9, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':3, 'isInlaw':false},
        {'id':10, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':3, 'isInlaw':true},
        {'id':11, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':2, 'isInlaw':true},
        {'id':12, 'sex': 'female', 'afflicted':false, 'children':[14, 15], 'partner': 13, 'level':3, 'isInlaw':false},
        {'id':13, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':3, 'isInlaw':true},
        {'id':14, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':15, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':16, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':2, 'isInlaw':true},
        {'id':17, 'sex': 'female', 'afflicted':false, 'children':[19, 20, 21, 22], 'partner': 18, 'level':3, 'isInlaw':false},
        {'id':18, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':3, 'isInlaw':true},
        {'id':19, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':20, 'sex': 'male', 'afflicted':true, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':21, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':22, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
        {'id':23, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':2, 'isInlaw':true},
        {'id':24, 'sex': 'male', 'afflicted':false, 'children':[], 'partner': null, 'level':3, 'isInlaw':false},
        {'id':25, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':3, 'isInlaw':false},
        {'id':26, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':3, 'isInlaw':false},
        {'id':27, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':3, 'isInlaw':false},

//        {'id':28, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':2, 'isInlaw':false},

//        {'id':29, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':2, 'isInlaw':false},
//        {'id':30, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},
//        {'id':31, 'sex': 'female', 'afflicted':false, 'children':[], 'partner': null, 'level':4, 'isInlaw':false},







        ],
    'adam':1
}

pedigreeJson =  JSON.parse(document.getElementById('jPedigree').textContent);
consistentPerInferrer = JSON.parse(document.getElementById('jConsPerInferrer').textContent);
possGensPerInferrer = JSON.parse(document.getElementById('jPossGensPerInferrer').textContent);

var pedigree = null;
var pd = null;

var canvDrag = {'isDragging': false,
               'prevMousePos': null,
               'overOrgCell': null,
               'overGenCell': null
               };

//var showGenotypes = false;

window.onresize = function () {
    canvasEl = document.getElementById('canvas');
    fitToContainer(canvasEl);
    var resize = true;
    pd.drawStuff(resize);
}



window.onload = function(){
    var inhPatternsEl = document.getElementById('id_inh_patterns');
    inhPatternsEl.addEventListener('change', inhPatternSelected, false);

    var numCons = numConsistent();
    var numExistEl = document.getElementById('num-exist');
    numExistEl.innerHTML = '(' + numCons + ' consistent pattern' + (numCons == 1 ? '' : 's') + ' exist' + (numCons == 1 ? 's' : '') + ')'

    var canvasEl = document.getElementById('canvas');
    //fitToContainer(canvasEl);
    canvasEl.addEventListener('mousedown', canvasMouseDown, false);
    canvasEl.addEventListener('mousemove', canvasMouseMove, false);
    canvasEl.addEventListener('mouseup', canvasMouseUp, false);


    pedigree = new Pedigree(pedigreeJson);
    pd = new PedigreeDiagram(pedigree,canvasEl, null);

    pd.drawStuff()

}

var orgs = JSON.parse(document.getElementById('jOrgs').textContent);
var state = 1;

