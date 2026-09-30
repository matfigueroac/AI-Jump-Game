const fs=require('fs');
let html='';
const app={set innerHTML(v){html=String(v)},get innerHTML(){return html}};
global.document={
  hidden:false,
  getElementById(id){return id==='app'?app:null},
  addEventListener(){},
  querySelector(){return null},
  querySelectorAll(){return []}
};
global.localStorage={getItem(){return null},setItem(){}};
global.navigator={vibrate(){}};
global.location={protocol:'file:',hostname:''};
global.window=global;
global.requestAnimationFrame=(fn)=>fn();
global.setInterval=()=>0;
global.setTimeout=()=>0;
global.Image=class{constructor(){this.complete=false;this.decode=null}set src(v){this._src=v}get src(){return this._src}};
let src=fs.readFileSync('web/app.js','utf8');
src=src.replace(/\}\)\(\);\s*$/, "globalThis.__slideTest={handle,state,render,dailyPuzzle};})();");
try{eval(src)}catch(e){console.error('LOAD ERROR',e.stack);process.exit(2)}
const assert=(c,m)=>{if(!c){console.error('ASSERT FAIL',m);process.exit(3)}};
assert(html.includes('PICK · SLIDE · SOLVE'),'home');
assert(html.includes('brand-lockup'),'brand');
assert(html.includes('PLAY DAILY PICK'),'daily');
const T=global.__slideTest;
T.handle('collection',{dataset:{}});
assert(html.includes('COLLECTIONS'),'collection');
T.handle('filter',{dataset:{filter:'all'}});
assert((html.match(/class="card"/g)||[]).length===43,'43 cards');
T.handle('filter',{dataset:{filter:'fantasy'}});
assert((html.match(/class="card"/g)||[]).length===10,'fantasy cards');
T.handle('play',{dataset:{id:'fantasy-01'}});
assert(html.includes('game-screen'),'game');
assert((html.match(/class="tile/g)||[]).length===16,'4x4');
T.handle('guide',{dataset:{}});
assert(html.includes('QUICK GUIDE'),'guide');
assert(!html.includes('ORIGINAL IMAGE'),'old guide');
T.handle('close-guide',{dataset:{}});
T.handle('collection',{dataset:{}});
T.handle('home',{dataset:{}});
T.handle('info',{dataset:{}});
assert(html.includes('HOW TO PLAY'),'howto');
console.log('PASS Slide Tales UI runtime smoke');
